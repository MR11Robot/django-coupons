from django.urls import path
from . import views


app_name = 'keyword_scrapper'



urlpatterns = [
    path('', views.KeywordScrapperControlView.as_view(), name='keyword_scrapper_control'),

]   