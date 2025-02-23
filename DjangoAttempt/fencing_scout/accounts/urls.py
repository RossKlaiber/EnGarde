from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # When you navigate to /login/ this custom login view is used.
    path('signup/', views.signup, name='signup'),
    path('', views.CustomLoginView.as_view(), name='login'),
    
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Password reset endpoints (using your existing templates)
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
    
    # Home pages for each user type (these will be used for redirection after login)
    path('athlete_home/', views.athlete_home, name='athlete_home'),
    path('recruiter_home/', views.recruiter_home, name='recruiter_home'),
]
