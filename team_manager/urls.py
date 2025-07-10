from django.urls import path
from . import views

app_name = 'team_manager'

urlpatterns = [
    path('', views.index, name='index'),
    path('upload_csv/', views.upload_csv, name='upload_csv'),
    path('send_discord/', views.send_discord, name='send_discord'),
] 