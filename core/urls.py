from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.HomeView.as_view(), name="home"),
    path("users/", include('users.urls')),
    
    path('coupon-checker/', include('coupon_checker.urls')),
    path('keyword-scrapper/', include('keyword_scrapper.urls')),
    path('backlink_checker/', include('link_checker.urls')),
    path('api/coupon-checker/', include('coupon_checker.apis.urls')),
]
