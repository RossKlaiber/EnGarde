from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_athlete_profile, name='create_athlete_profile'),
    path('', views.add_profile_information, name='add_profile_information'),
    path('view_profile/', views.view_profile, name='view_profile'),
    path('add_view_recruiters/', views.add_view_recruiters, name='add_view_recruiters'),
    
]
