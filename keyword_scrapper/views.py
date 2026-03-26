from django.conf import settings
import requests
from django.views.generic import View
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse

class KeywordScrapperControlView(LoginRequiredMixin, View):
    template_name = "keyword_scrapper/control.html"
    base_api_url = settings.KEYWORD_SCRAPPER_API_URL
    
    def get_status(self):
        try:
            response = requests.get(f"{self.base_api_url}/status/")
            response.raise_for_status()
            data = response.json()
            data["status"] = "running" if data.get("status", False) else "stopped"
            data["current_country_progress"] = str(data.get("current_country_progress", "N/A"))
            return data
        except requests.RequestException as e:
            return {
                "status": "unknown",
                "started_at": None,
                "current_keyword": None,
                "current_country": None,
                "current_country_progress": "N/A",
                "finished_at": None,
                "message": "Error fetching status"
            }

    def get(self, request, *args, **kwargs):
        status_data = self.get_status()
        
        # Handle download request
        if "download" in request.GET:
            try:
                response = requests.get(f"{self.base_api_url}/download/")
                response.raise_for_status()
                return HttpResponse(
                    response.content,
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    headers={'Content-Disposition': 'attachment; filename="Keywords_Report.xlsx"'}
                )
            except requests.RequestException as e:
                status_data["message"] = f"Failed to download file: {str(e)}"
        
        context = {"status": status_data}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        status_data = self.get_status()

        if "start" in request.POST:
            try:
                response = requests.post(f"{self.base_api_url}/start/")
                response.raise_for_status()
            except requests.RequestException as e:
                status_data["message"] = f"Failed to start bot: {str(e)}"

        elif "stop" in request.POST:
            try:
                response = requests.post(f"{self.base_api_url}/stop/")
                response.raise_for_status()
            except requests.RequestException as e:
                status_data["message"] = f"Failed to stop bot: {str(e)}"

        return redirect(reverse('keyword_scrapper:keyword_scrapper_control'))