from django.urls import path
from .views import BacklinkCheckerControlView, EditWebsiteView, AddWebsiteView

app_name = "backlink_checker"

urlpatterns = [
    path('control/', BacklinkCheckerControlView.as_view(), name='control'),
    path('edit/<str:name>/', EditWebsiteView.as_view(), name='edit_website'),
    path('add/', AddWebsiteView.as_view(), name='add_website'),
]