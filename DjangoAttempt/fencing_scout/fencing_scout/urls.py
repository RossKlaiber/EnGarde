from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    # Redirect the root URL to /login/
    path('', RedirectView.as_view(url='/login/', permanent=False)),
    path('admin/', admin.site.urls),
    # Include account-related URLs under /login/
    path('login/', include('accounts.urls')),
    path('profiles/', include('profiles.urls')),

]
