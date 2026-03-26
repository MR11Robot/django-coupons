import requests
import re
from django.views.generic import View
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.contrib import messages
from django.conf import settings




class BacklinkCheckerControlView(LoginRequiredMixin, View):
    template_name = "backlink_checker/control.html"
    base_api_url = settings.BACKLINK_CHECKER_API_URL

    def get_status(self):
        try:
            response = requests.get(f"{self.base_api_url}/status/")
            response.raise_for_status()
            data = response.json()                
            
            data["status"] = "running" if data.get("status", False) else "stopped"
            data["current_website_name"] = data.get("current_website_name", "N/A")
            data["current_website_number"] = data.get("current_website_number", 0)
            data["total_articles_in_website"] = data.get("total_articles_in_website", 0)
            data["current_link_number"] = data.get("current_link_number", 0)
            return data
        except requests.RequestException as e:
            return {
                "status": "unknown",
                "started_at": None,
                "current_website_name": "N/A",
                "current_website_number": 0,
                "total_articles_in_website": 0,
                "current_link_number": 0,
                "finished_at": None,
                "message": "Error fetching status"
            }

    def get_websites(self):
        try:
            response = requests.get(f"{self.base_api_url}/websites/")
            response.raise_for_status()
            return response.json().get("websites", [])
        except requests.RequestException:
            return []

    def get(self, request, *args, **kwargs):
        status_data = self.get_status()
        websites = self.get_websites()
        
        # Handle download request
        if "download" in request.GET:
            filename = request.GET.get("filename")
            if filename:
                try:
                    response = requests.get(f"{self.base_api_url}/download/{filename}/")
                    response.raise_for_status()
                    return HttpResponse(
                        response.content,
                        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        headers={'Content-Disposition': f'attachment; filename="{filename}.xlsx"'}
                    )
                except requests.RequestException as e:
                    status_data["message"] = f"Failed to download file: {str(e)}"
        
        context = {
            "status": status_data,
            "websites": websites
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        status_data = self.get_status()

        if "start" in request.POST:
            try:
                response = requests.post(f"{self.base_api_url}/start/")
                response.raise_for_status()
                messages.success(request, "Bot started successfully")
            except requests.RequestException as e:
                messages.error(request, f"Failed to start bot: {str(e)}")

        elif "stop" in request.POST:
            try:
                response = requests.post(f"{self.base_api_url}/stop/")
                response.raise_for_status()
                messages.success(request, "Bot stopped successfully")
            except requests.RequestException as e:
                messages.error(request, f"Failed to stop bot: {str(e)}")

        return redirect(reverse('backlink_checker:control'))
    
class EditWebsiteView(LoginRequiredMixin, View):
    template_name = "backlink_checker/update/edit.html"
    base_api_url = settings.BACKLINK_CHECKER_API_URL

    def get(self, request, name, *args, **kwargs):
        websites = self.get_websites()
        website = next((w for w in websites if w["name"] == name), None)
        if not website:
            messages.error(request, f"Website {name} not found")
            return redirect(reverse('backlink_checker:control'))

        context = {"website": website}
        return render(request, self.template_name, context)

    def post(self, request, name, *args, **kwargs):
        # Check if this is a delete request
        if "delete" in request.POST:
            try:
                response = requests.delete(f"{self.base_api_url}/delete_website/{name}/")
                response.raise_for_status()
                messages.success(request, f"Website {name} deleted successfully")
                return redirect(reverse('backlink_checker:control'))
            except requests.RequestException as e:
                messages.error(request, f"Failed to delete website: {str(e)}")
                return redirect(reverse('backlink_checker:control'))

        # Handle update request
        data = {
            "name": request.POST.get("name"),
            "domain": request.POST.get("domain"),
            "spreadsheet_id": request.POST.get("spreadsheet_id"),
            "row_range": request.POST.get("row_range"),
            "app_link": request.POST.get("app_link"),
            "link_location": int(request.POST.get("link_location", 0)),
            "aliases": [alias.strip() for alias in request.POST.getlist("aliases[]") if alias.strip()]
        }
        try:
            response = requests.put(f"{self.base_api_url}/update_website/{name}/", json=data)
            response.raise_for_status()
            messages.success(request, f"Website {name} updated successfully")
        except requests.RequestException as e:
            messages.error(request, f"Failed to update website: {str(e)}")
        return redirect(reverse('backlink_checker:control'))

    def get_websites(self):
        try:
            response = requests.get(f"{self.base_api_url}/websites/")
            response.raise_for_status()
            return response.json().get("websites", [])
        except requests.RequestException:
            return []
class AddWebsiteView(LoginRequiredMixin, View):
    template_name = "backlink_checker/create/add_website.html"
    base_api_url = settings.BACKLINK_CHECKER_API_URL

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        data = {
            "name": request.POST.get("name", "").strip(),
            "domain": request.POST.get("domain", "").strip(),
            "spreadsheet_id": request.POST.get("spreadsheet_id", "").strip(),
            "row_range": request.POST.get("row_range", "").strip(),
            "link_location": request.POST.get("link_location", ""),
            "app_link": request.POST.get("app_link", "").strip(),
            "aliases": [alias.strip() for alias in request.POST.getlist("aliases[]") if alias.strip()]
        }

        # Handle app_link (optional)
        app_link = request.POST.get("app_link", "").strip()
        if app_link:  # Only add app_link if it's not empty or whitespace
            data["app_link"] = app_link

        # Validation
        errors = {}
        if not data["name"]:
            errors["name"] = "Website name is required."
        elif data["name"].isspace():
            errors["name"] = "Website name cannot be just spaces."
            
        if not data["domain"]:
            errors["domain"] = "Domain is required."
        elif data["domain"].isspace():
            errors["domain"] = "Domain cannot be just spaces."
        elif not re.match(r"^(https?:\/\/)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$", data["domain"]):
            errors["domain"] = "Invalid domain format."
        

        if not data["spreadsheet_id"] and not data["spreadsheet_id"].isspace():
            errors["spreadsheet_id"] = "Spreadsheet ID is required."
        
            
        if not data["row_range"]:
            errors["row_range"] = "Row range is required."
        elif data["row_range"].isspace():
            errors["row_range"] = "Row range cannot be just spaces."
        elif not re.match(r"^[A-Z]+[0-9]+:[A-Z]+[0-9]+$", data["row_range"]):
            errors["row_range"] = "Invalid row range format (e.g., A1:B10)."
        
        if data["app_link"] and not data["app_link"].isspace():
            if re.match(r"^https?:\/\/", data["app_link"]):
                errors["app_link"] = "App link must be a valid URL starting with http:// or https://."

        # Validate link_location
        if not data["link_location"]:
            errors["link_location"] = "Link location is required."
        elif not data["link_location"].isdigit():
            errors["link_location"] = "Link location must be a valid number."
        else:
            data["link_location"] = int(data["link_location"])
            if data["link_location"] <= 0:
                errors["link_location"] = "Link location must be greater than 0."

        if errors:
            for field, error in errors.items():
                messages.error(request, error)
            return render(request, self.template_name, {"form_data": data})

        # If validation passes, send to API
        try:
            response = requests.post(f"{self.base_api_url}/add_website/", json=data)
            response.raise_for_status()
            messages.success(request, f"Website {data['name']} added successfully")
            return redirect(reverse('backlink_checker:control'))
        except requests.RequestException as e:
            messages.error(request, f"Failed to add website: {str(e)}")
            return render(request, self.template_name, {"form_data": data})