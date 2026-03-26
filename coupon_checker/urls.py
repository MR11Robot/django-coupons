from django.urls import path
from . import views
from uuid import UUID


app_name = 'coupon_checker'


urlpatterns = [
    path('', views.CouponCheckerView.as_view(), name='coupon_checker'),

    path('websites/', views.WebsiteView.as_view(), name='websites'),
    path('websites/create/', views.WebsiteCreateView.as_view(), name='website_create'),
    path("websites/<slug:website_slug>/edit/", views.WebsiteUpdateView.as_view(), name="website_edit"),
    path("websites/<slug:website_slug>/delete/", views.WebsiteDeleteView.as_view(), name="website_delete"),
    
    path('websites/<slug:website_slug>/stores/', views.WebsiteStoresView.as_view(), name='website_stores'),
    path("websites/<slug:website_slug>/stores/add/", views.StoreCreateView.as_view(), name="store_create"),
    path('websites/<slug:website_slug>/stores/<slug:store_slug>/edit/', views.StoreUpdateView.as_view(), name='store_edit'),
    path("websites/<slug:website_slug>/stores/<slug:store_slug>/delete/", views.StoreDeleteView.as_view(), name="store_delete"),

    path('websites/<slug:website_slug>/stores/<slug:store_slug>/coupons/', views.StoreCouponsView.as_view(), name='store_coupons'),
    path("websites/<slug:website_slug>/stores/<slug:store_slug>/coupons/add/", 
        views.CouponCreateView.as_view(), 
        name="coupon_create",
    ),
    path("websites/<slug:website_slug>/stores/<slug:store_slug>/coupons/<uuid:pk>/edit/", views.CouponUpdateView.as_view(), name="coupon_edit"),
    path("websites/<slug:website_slug>/stores/<slug:store_slug>/coupons/<uuid:pk>/delete/", views.CouponDeleteView.as_view(), name="coupon_delete"),

    path('companies/', views.CompanyListView.as_view(), name='company_list'),
    path('companies/add/', views.AddCompanyView.as_view(), name='company_create'),
    path('companies/edit/<uuid:pk>/', views.EditCompanyView.as_view(), name='company_update'),

    path('countries/', views.CountryListView.as_view(), name='country_list'),
    path('countries/add/', views.AddCountryView.as_view(), name='country_create'),
    path('countries/edit/<uuid:pk>/', views.EditCountryView.as_view(), name='country_update'),

    path('reports/', 
        views.CouponReportsView.as_view(), 
        name='coupon_reports'),
]   