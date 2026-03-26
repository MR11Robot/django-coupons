from django.contrib.auth.models import Group, User
from rest_framework import serializers
from ..models import Company, Country, Coupon, Store, Website, CouponReport
import uuid

        

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'slug', 'created_at', 'updated_at']

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name', 'code', 'created_at', 'updated_at']
        

class WebsiteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Website
        fields = ['id', 'name', 'slug', 'url']
     
class StoreSerializer(serializers.ModelSerializer):
    website = WebsiteSerializer()
    class Meta:
        model = Store
        fields = ['id', 'name', 'slug', 'url', 'check_status', 'website']
           
class CouponSerializer(serializers.ModelSerializer):
    company = CompanySerializer()
    countries = CountrySerializer(many=True)
    store = StoreSerializer()
    class Meta:
        model = Coupon
        fields = ['id', 'code', 'store', 'company', 'check_status', 'countries', 'created_at', 'updated_at']
    

class CouponReportSerializer(serializers.ModelSerializer):
    coupon = serializers.PrimaryKeyRelatedField(queryset=Coupon.objects.all())

    class Meta:
        model = CouponReport
        fields = ['id', 'coupon', 'status', 'discount', 'product_link', 'last_check', 'checked_country']
        
