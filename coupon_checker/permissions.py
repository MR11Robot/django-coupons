from rest_framework_api_key.permissions import BaseHasAPIKey
from rest_framework_api_key.models import APIKey

class HasCouponCheckerAPIKey(BaseHasAPIKey):
    model = APIKey

    def has_permission(self, request, view):
        api_key = request.headers.get("Authorization", "").replace("Api-Key ", "")
        if not api_key:
            return False
        
        try:
            api_key_obj = APIKey.objects.get_from_key(api_key)
            return api_key_obj.name == "Coupon-Checker"
        except APIKey.DoesNotExist:
            return False
