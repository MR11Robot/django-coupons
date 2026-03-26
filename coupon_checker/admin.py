from django.contrib import admin
from .models import Website, Coupon, Store, Country, Company, CouponReport
from django.forms import ModelForm
from django.forms import CheckboxSelectMultiple


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name',)
    prepopulated_fields = {'slug': ('name',)}



class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'store', 'get_countries', 'check_status', 'updated_at')  
    search_fields = ('code', 'store__name')
    list_filter = ('created_at', 'updated_at', 'check_status', 'store__name', 'store__website__name')
    ordering = ('-created_at',)
    autocomplete_fields = ['store']
    readonly_fields = ('id','created_at', 'updated_at')  
    fields = ('id', 'code', 'store', 'company', 'check_status', 'countries')

    def get_countries(self, obj):
        return ", ".join([country.code for country in obj.countries.all()])
    get_countries.short_description = 'Countries'

class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'updated_at')
    search_fields = ('name', 'url')
    ordering = ('-created_at',)
    list_filter = ('website',)
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')

    
class WebsiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('url', 'name')
    ordering = ('-created_at',)
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    

class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at', 'updated_at')
    readonly_fields = ('id', 'created_at', 'updated_at')
    fields = ('id', 'name', 'code', 'created_at', 'updated_at')
    


class StoreCountryAdmin(admin.ModelAdmin):
    list_display = ('store', 'country', 'url')


class CouponReportAdmin(admin.ModelAdmin):
    list_display = ('coupon', 'coupon__store__name', 'coupon__store__website', 'last_check')  # إضافة الحقل store إلى العرض
    list_filter = ('coupon__store__website', 'last_check', 'checked_country', 'coupon__store')
    
        
        

admin.site.register(CouponReport, CouponReportAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(Website, WebsiteAdmin)
admin.site.register(Store, StoreAdmin)
admin.site.register(Country, CountryAdmin)

