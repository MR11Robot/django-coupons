from django.urls import path
from . import views
from coupon_checker.apis import views as api_views
from rest_framework.routers import DefaultRouter



urlpatterns = [
    path("websites/", api_views.WebsiteListView.as_view(), name="website-list"),
    path("stores/", api_views.StoreListView.as_view(), name="store-list"),
    path("coupons/", api_views.CouponListView.as_view(), name="coupon-list"),
    path("reports/", api_views.CouponReportListView.as_view(), name="report-list"),
    
    path("stores/<slug:store_slug>/coupons/", api_views.StoreCouponsView.as_view(), name="store-coupons"),
]

