# coupon_checker/forms.py
from urllib.parse import urlparse
from django import forms
from django.template.defaultfilters import slugify
from django.core.exceptions import ValidationError

import re

from .models import Website, Store, Coupon, Company, Country
class WebsiteForm(forms.ModelForm):
    class Meta:
        model = Website
        fields = ['name','url']  # Only editable fields
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make name and slug optional since save() can generate them
        self.fields['name'].required = True


    def clean_name(self):
        """Allow only English letters, numbers, and dashes."""
        name = self.cleaned_data.get("name")
        if not re.match(r"^[a-zA-Z0-9- ]+$", name):  
            raise forms.ValidationError("Only English letters, numbers, spaces, and dashes are allowed.")
        return name

    def clean(self):
        """Reflect save() logic in validation."""
        cleaned_data = super().clean()
        url = cleaned_data.get('url')
        name = cleaned_data.get('name')

        # Preview auto-generation for validation
        if url and not name:
            cleaned_data['name'] = urlparse(url).netloc
        return cleaned_data
    
    
    
class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ["name", "website", "url", "check_status"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "website": forms.Select(attrs={"class": "form-control", "disabled": "disabled"}), 
            "url": forms.URLInput(attrs={"class": "form-control"}),
            "check_status": forms.Select(attrs={"class": "form-control"}),  
        }

    def __init__(self, *args, **kwargs):
        website = kwargs.pop("website", None)  
        self.instance = kwargs.get("instance")
        super().__init__(*args, **kwargs)

        if not self.instance:
            self.fields["name"].required = True
            self.fields["url"].required = True

        if website:
            self.fields["website"].initial = website 
            self.fields["website"].queryset = Website.objects.filter(id=website.id) 
        elif self.instance:
            self.fields["website"].initial = self.instance.website  

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        url = cleaned_data.get("url")
        website = cleaned_data.get("website")

        if self.instance:
            existing_store = Store.objects.filter(website=website, name=name).exclude(id=self.instance.id).exists()
            if existing_store:
                self.add_error("name", "A store with this name already exists for this website.")

            existing_url = Store.objects.filter(website=website, url=url).exclude(id=self.instance.id).exists()
            if existing_url:
                self.add_error("url", "A store with this URL already exists for this website.")
        else:
            if Store.objects.filter(website=website, name=name).exists():
                self.add_error("name", "A store with this name already exists for this website.")

            if Store.objects.filter(website=website, url=url).exists():
                self.add_error("url", "A store with this URL already exists for this website.")

        if url:
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                self.add_error("url", "Please enter a valid URL with a proper scheme (http or https).")

        return cleaned_data

class CouponForm(forms.ModelForm):
    website = forms.CharField(
        label="Website",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),
    )
    store = forms.ModelChoiceField(
        queryset=Store.objects.all(),
        widget=forms.HiddenInput(),  
    )

    class Meta:
        model = Coupon
        fields = ["code", "company", "check_status", "countries", "store"]

        widgets = {
            "code": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter coupon code"}),
            "company": forms.Select(attrs={"class": "form-select"}),
            "check_status": forms.Select(attrs={"class": "form-select"}),
            "countries": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, store=None, **kwargs):
        super().__init__(*args, **kwargs)
        if store:
            self.fields['store'].initial = store 