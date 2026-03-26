from django.shortcuts import get_object_or_404, redirect
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.urls import reverse
from datetime import timedelta
from django.utils import timezone
from django.utils.dateparse import parse_date

from .models import Country, Coupon, Website, Store, CouponReport, Company
from .forms import WebsiteForm, StoreForm, CouponForm


class StoreCouponsView(LoginRequiredMixin, ListView):
    model = Coupon
    template_name = "coupon_checker/store_coupons.html"
    context_object_name = "coupons"
    paginate_by = 10

    def get_queryset(self):
        website_slug = self.kwargs.get("website_slug")
        store_slug = self.kwargs.get("store_slug")
        
        search_query = self.request.GET.get('search', '').strip()
        status_filter = self.request.GET.get('status', '')
        
        website = get_object_or_404(Website, slug=website_slug)
        store = get_object_or_404(
            Store,
            website=website,
            slug=store_slug
        )
        
        queryset = store.coupons.all()
        
        if search_query:
            queryset = queryset.filter(code__icontains=search_query)
        
        if status_filter:
            queryset = queryset.filter(check_status=status_filter)
            
        return queryset.order_by('-updated_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["store"] = get_object_or_404(
            Store,
            website__slug=self.kwargs.get("website_slug"),
            slug=self.kwargs.get("store_slug")
        )
        
        context["search_query"] = self.request.GET.get('search', '').strip()
        context["status_filter"] = self.request.GET.get('status', '')
        
        return context
    

class WebsiteView(LoginRequiredMixin, ListView):
    """Handle listing and creating websites in a single view."""
    model = Website
    template_name = "coupon_checker/websites.html"
    context_object_name = "websites"
    paginate_by = 10
    success_url = reverse_lazy('coupon_checker:websites')

    def get_queryset(self):
        """Return the queryset for websites, ordered by name."""
        return Website.objects.all().order_by('name')

    def get_context_data(self, **kwargs):
        """Add the form to the context for rendering."""
        context = super().get_context_data(**kwargs)
        context['form'] = kwargs.get('form', WebsiteForm())
        return context

    def post(self, request, *args, **kwargs):
        """Handle form submission to create a new website."""
        form = WebsiteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Website added successfully!")
            return self._success_redirect()
        return self._render_with_errors(form)

    def _success_redirect(self):
        """Redirect to the success URL after a successful form submission."""
        return redirect(self.success_url)

    def _render_with_errors(self, form):
        """Re-render the page with form errors if validation fails."""
        self.object_list = self.get_queryset()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)


class CouponCheckerView(LoginRequiredMixin, ListView):
    model = Website
    template_name = "coupon_checker/coupon_checker.html"
    context_object_name = "websites"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["countries"] = Country.objects.all()  
        context["companies"] = Company.objects.all()  
        return context

class WebsiteStoresView(LoginRequiredMixin, ListView):
    model = Store
    template_name = "coupon_checker/website_stores.html"
    context_object_name = "stores"
    paginate_by = 10

    def get_queryset(self):
        website_slug = self.kwargs.get("website_slug") 
        website = get_object_or_404(Website, slug=website_slug)
        
        search_query = self.request.GET.get('search', '').strip()
        status_filter = self.request.GET.get('status', '')
        
        queryset = Store.objects.filter(website=website)
        
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        
        if status_filter:
            queryset = queryset.filter(check_status=status_filter)
            
        return queryset.order_by('updated_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["website"] = get_object_or_404(Website, slug=self.kwargs.get("website_slug"))
        
        context["search_query"] = self.request.GET.get('search', '').strip()
        context["status_filter"] = self.request.GET.get('status', '')
        
        return context

class CouponUpdateView(LoginRequiredMixin, UpdateView):
    model = Coupon
    form_class = CouponForm
    template_name = "coupon_checker/update/coupon_update.html"
    context_object_name = "coupon"

    def get_object(self, queryset=None):
        print(f"Kwargs: {self.kwargs}") 

        website_slug = self.kwargs.get("website_slug")
        store_slug = self.kwargs.get("store_slug") 
        coupon_id = self.kwargs.get("pk")

        return get_object_or_404(
            Coupon, store__website__slug=website_slug, store__slug=store_slug, id=coupon_id
        )
    def form_valid(self, form):
        messages.success(self.request, "Coupon updated successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse("coupon_checker:store_coupons", kwargs={
            "website_slug": self.object.store.website.slug,
            "store_slug": self.object.store.slug
        })

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["store"] = self.object.store
        return kwargs

class StoreUpdateView(LoginRequiredMixin, UpdateView):
    model = Store
    form_class = StoreForm
    template_name = "coupon_checker/update/store_update.html"
    context_object_name = "store"

    def get_object(self, queryset=None):
        website_slug = self.kwargs.get("website_slug")
        store_slug = self.kwargs.get("store_slug")
        return get_object_or_404(Store, website__slug=website_slug, slug=store_slug)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["website"] = self.get_object().website
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Store updated successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse("coupon_checker:website_stores", kwargs={"website_slug": self.object.website.slug})

    
class WebsiteCreateView(LoginRequiredMixin, CreateView):
    """Handle the creation of a new website."""
    model = Website
    form_class = WebsiteForm
    template_name = "coupon_checker/create/website_create.html"
    success_url = reverse_lazy('coupon_checker:websites')

    def form_valid(self, form):
        """Save the form and add a success message."""
        response = super().form_valid(form)
        messages.success(self.request, "Website added successfully!")
        return response



    
class StoreCreateView(LoginRequiredMixin, CreateView):
    """Handle the creation of a new store."""
    model = Store
    form_class = StoreForm
    template_name = "coupon_checker/create/store_create.html"
    success_url = reverse_lazy('coupon_checker:website_stores')

    
    def form_valid(self, form):
        """Save the form and add a success message."""
        response = super().form_valid(form)
        messages.success(self.request, "Store added successfully!")
        return response

    def get_success_url(self):
        """Redirect to the website stores page after success."""
        return reverse_lazy("coupon_checker:website_stores", kwargs={"website_slug": self.kwargs.get("website_slug")})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        website = get_object_or_404(Website, slug=self.kwargs["website_slug"]) 
        kwargs["website"] = website
        return kwargs

    def get_context_data(self, **kwargs):
        """Pass additional context to the template."""
        context = super().get_context_data(**kwargs)
        website_slug = self.kwargs.get("website_slug")
        website = get_object_or_404(Website, slug=website_slug)
        context["website"] = website
        return context
    
    
class WebsiteUpdateView(LoginRequiredMixin, UpdateView):
    model = Website
    form_class = WebsiteForm
    template_name = "coupon_checker/update/website_update.html"
    slug_field = "slug"
    slug_url_kwarg = "website_slug"


    def post(self, request, *args, **kwargs):
        """Handle POST request manually to debug."""
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
        
    def form_valid(self, form):
        """Check if name is valid before updating slug."""
        website = form.save(commit=False)

        try:
            new_slug = slugify(website.name)
            if not new_slug:
                raise ValidationError("Invalid website name. Please use only English letters, numbers, and dashes.")

            if new_slug != website.slug:
                website.slug = new_slug

            website.save()
            messages.success(self.request, "Website updated successfully!")
            return super().form_valid(form)

        except ValidationError as e:
            form.add_error("name", e)  # Add error to form
            return self.form_invalid(form)  # Render form with errors

    def get_success_url(self):
        return reverse_lazy("coupon_checker:websites")
    
class WebsiteDeleteView(LoginRequiredMixin, DeleteView):
    model = Website
    slug_field = "slug"
    slug_url_kwarg = "website_slug"
    success_url = reverse_lazy("coupon_checker:websites") 

    def delete(self, request, *args, **kwargs):
        website = self.get_object()
        messages.success(request, f"Website '{website.name}' has been deleted successfully.")
        return super().delete(request, *args, **kwargs)
    

class StoreDeleteView(LoginRequiredMixin, DeleteView):
    model = Store
    slug_field = "slug"
    slug_url_kwarg = "store_slug"

    def get_queryset(self):
        website_slug = self.kwargs.get("website_slug")
        website = get_object_or_404(Website, slug=website_slug)
        return Store.objects.filter(website=website)

    def get_success_url(self):
        return reverse_lazy("coupon_checker:website_stores", kwargs={"website_slug": self.object.website.slug})

    def delete(self, request, *args, **kwargs):
        store = self.get_object()
        messages.success(request, f"Store '{store.name}' has been deleted successfully.")
        return super().delete(request, *args, **kwargs)
class CouponDeleteView(LoginRequiredMixin, DeleteView):
    model = Coupon
    slug_field = "slug"
    slug_url_kwarg = "coupon_slug"

    def get_success_url(self):
        return reverse_lazy(
            "coupon_checker:store_coupons",
            kwargs={
                "website_slug": self.object.store.website.slug,
                "store_slug": self.object.store.slug,
            },
        )

    def delete(self, request, *args, **kwargs):
        coupon = self.get_object()
        print(f"Deleting coupon: {coupon.code}, Store: {coupon.store}")  # Debugging
        messages.success(request, f"Coupon '{coupon.code}' has been deleted successfully.")
        return super().delete(request, *args, **kwargs)

class CouponCreateView(LoginRequiredMixin, CreateView):
    model = Coupon
    form_class = CouponForm
    template_name = "coupon_checker/create/coupon_create.html"

    def get_success_url(self):
        website_slug = self.kwargs.get("website_slug")
        store_slug = self.kwargs.get("store_slug")
        return reverse("coupon_checker:store_coupons", kwargs={"website_slug": website_slug, "store_slug": store_slug})

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        website_slug = self.kwargs.get("website_slug")
        store_slug = self.kwargs.get("store_slug")

        website = get_object_or_404(Website, slug=website_slug)
        store = get_object_or_404(Store, website=website, slug=store_slug)

        form.store = store
        form.fields["store"].initial = store.name
        form.fields["website"].initial = website.name

        return form

    def form_valid(self, form):
        store = self.get_store()  
        form.instance.store = store 
        
        print("Saving Coupon with Store:", store)
        
        return super().form_valid(form)

    def get_store(self):
        website_slug = self.kwargs.get("website_slug")
        store_slug = self.kwargs.get("store_slug")

        website = get_object_or_404(Website, slug=website_slug)
        store = get_object_or_404(Store, website=website, slug=store_slug)

        return store



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        website_slug = self.kwargs.get("website_slug")
        store_slug = self.kwargs.get("store_slug")

        website = get_object_or_404(Website, slug=website_slug)
        store = get_object_or_404(Store, website=website, slug=store_slug)

        context["store"] = store
        context["website"] = website

        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        website_slug = self.kwargs.get("website_slug")
        store_slug = self.kwargs.get("store_slug")

        website = get_object_or_404(Website, slug=website_slug)
        store = get_object_or_404(Store, website=website, slug=store_slug)

        kwargs["store"] = store
        return kwargs
    

class CompanyListView(LoginRequiredMixin, ListView):
    model = Company
    template_name = "coupon_checker/company_list.html"
    context_object_name = "companies"
    paginate_by = 10

    def get_queryset(self):
        search_query = self.request.GET.get('search', '').strip()
        date_filter = self.request.GET.get('date_filter', '')

        queryset = Company.objects.all()

        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        if date_filter:
            now = timezone.now()
            if date_filter == 'today':
                queryset = queryset.filter(created_at__date=now.date())
            elif date_filter == 'yesterday':
                queryset = queryset.filter(created_at__date=now.date() - timedelta(days=1))
            elif date_filter == 'last_7_days':
                queryset = queryset.filter(created_at__gte=now - timedelta(days=7))
            elif date_filter == 'last_30_days':
                queryset = queryset.filter(created_at__gte=now - timedelta(days=30))

        return queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get('search', '').strip()
        context["date_filter"] = self.request.GET.get('date_filter', '')
        return context

class AddCompanyView(LoginRequiredMixin, CreateView):
    model = Company
    template_name = "coupon_checker/create/company_create.html"
    fields = ['name']
    success_url = reverse_lazy('coupon_checker:company_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Company '{self.object.name}' added successfully!")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Failed to add company. Please check the form.")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_data'] = self.request.POST if self.request.method == 'POST' else {}
        return context

class EditCompanyView(LoginRequiredMixin, UpdateView):
    model = Company
    template_name = "coupon_checker/update/company_update.html"
    fields = ['name']
    success_url = reverse_lazy('coupon_checker:company_list')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if "delete" in request.POST:
            company_name = self.object.name
            self.object.delete()
            messages.success(request, f"Company '{company_name}' deleted successfully!")
            return redirect(self.success_url)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Company '{self.object.name}' updated successfully!")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Failed to update company. Please check the form.")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = self.object
        return context

class CountryListView(LoginRequiredMixin, ListView):
    model = Country
    template_name = "coupon_checker/country_list.html"
    context_object_name = "countries"
    paginate_by = 10

    def get_queryset(self):
        search_query = self.request.GET.get('search', '').strip()
        date_filter = self.request.GET.get('date_filter', '')

        queryset = Country.objects.all()

        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        if date_filter:
            now = timezone.now()
            if date_filter == 'today':
                queryset = queryset.filter(created_at__date=now.date())
            elif date_filter == 'yesterday':
                queryset = queryset.filter(created_at__date=now.date() - timedelta(days=1))
            elif date_filter == 'last_7_days':
                queryset = queryset.filter(created_at__gte=now - timedelta(days=7))
            elif date_filter == 'last_30_days':
                queryset = queryset.filter(created_at__gte=now - timedelta(days=30))

        return queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get('search', '').strip()
        context["date_filter"] = self.request.GET.get('date_filter', '')
        return context
    
    
class AddCountryView(LoginRequiredMixin, CreateView):
    model = Country
    template_name = "coupon_checker/create/country_create.html"
    fields = ['code', 'name']
    success_url = reverse_lazy('coupon_checker:country_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Country '{self.object.name}' added successfully!")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Failed to add country. Please check the form.")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_data'] = self.request.POST if self.request.method == 'POST' else {}
        return context

class EditCountryView(LoginRequiredMixin, UpdateView):
    model = Country
    template_name = "coupon_checker/update/country_update.html"
    fields = ['code', 'name']
    success_url = reverse_lazy('coupon_checker:country_list')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if "delete" in request.POST:
            country_name = self.object.name
            self.object.delete()
            messages.success(request, f"Country '{country_name}' deleted successfully!")
            return redirect(self.success_url)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Country '{self.object.name}' updated successfully!")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Failed to update country. Please check the form.")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['country'] = self.object
        return context
    
    
class CouponReportsView(LoginRequiredMixin, ListView):
    model = CouponReport
    template_name = "coupon_checker/report_list.html"
    context_object_name = "reports"
    paginate_by = 10

    def get_queryset(self):
        website_slug = self.request.GET.get('website', '')
        store_slug = self.request.GET.get('store', '')
        date_filter = self.request.GET.get('date', '')
        coupon_search = self.request.GET.get('coupon_search', '').strip()
        status_filter = self.request.GET.get('status', '')
        country_filter = self.request.GET.get('country', '')

        queryset = CouponReport.objects.all()

        if website_slug:
            try:
                website = Website.objects.get(slug=website_slug)
                queryset = queryset.filter(coupon__store__website=website)
            except Website.DoesNotExist:
                queryset = queryset.none()

        if store_slug:
            if website_slug:
                try:
                    website = Website.objects.get(slug=website_slug)
                    queryset = queryset.filter(coupon__store__slug=store_slug, coupon__store__website=website)
                except Website.DoesNotExist:
                    queryset = queryset.none()
            else:
                queryset = queryset.filter(coupon__store__slug=store_slug)

        if coupon_search:
            queryset = queryset.filter(coupon__code__icontains=coupon_search)
            

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        if country_filter:
            try:
                queryset = queryset.filter(checked_country__id=country_filter)
            except ValueError:
                messages.warning(self.request, "Invalid country filter.")

        if date_filter:
            try:
                filter_date = parse_date(date_filter)
                queryset = queryset.filter(last_check__date=filter_date)
            except ValueError:
                pass
        else:
            now = timezone.now()
            queryset = queryset.filter(last_check__date=now.date())

        return queryset.order_by('-last_check')
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['websites'] = Website.objects.all()
        
        website_slug = self.request.GET.get('website', '')
        if website_slug:
            website = get_object_or_404(Website, slug=website_slug)
            context['stores'] = Store.objects.filter(website=website)
            context['selected_website'] = website
        else:
            context['stores'] = Store.objects.all()
        
        context['countries'] = Country.objects.all()
        
        context['coupon_search'] = self.request.GET.get('coupon_search', '').strip()
        
        date_filter = self.request.GET.get('date', '')
        if not date_filter:
            today = timezone.localtime().date().strftime('%Y-%m-%d')
            context['date_filter'] = today
        else:
            context['date_filter'] = date_filter
            
        context['store_filter'] = self.request.GET.get('store', '')
        context['website_filter'] = website_slug
        context['status_filter'] = self.request.GET.get('status', '')
        context['country_filter'] = self.request.GET.get('country', '')
        
        store_slug = self.request.GET.get('store', '')
        if store_slug:
            try:
                if website_slug:
                    store = Store.objects.get(slug=store_slug, website__slug=website_slug)
                else:
                    store = Store.objects.filter(slug=store_slug).first()
                    
                context['store_filter_name'] = store.name if store else store_slug
            except Store.DoesNotExist:
                context['store_filter_name'] = store_slug
        
        country_id = self.request.GET.get('country', '')
        if country_id:
            try:
                country = Country.objects.get(id=country_id)
                context['country_filter_name'] = country.name
            except Country.DoesNotExist:
                context['country_filter_name'] = "Unknown Country"
        
        if date_filter:
            try:
                filter_date = parse_date(date_filter)
                total_reports_for_date = CouponReport.objects.filter(last_check__date=filter_date).count()
            except ValueError:
                total_reports_for_date = 0
        else:
            now = timezone.now()
            total_reports_for_date = CouponReport.objects.filter(last_check__date=now.date()).count()
        
        context['total_reports_for_date'] = total_reports_for_date
        
        return context