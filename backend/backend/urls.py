"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
"""from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin
from django.http import HttpResponse


def home(request):
    return HttpResponse("Welcome to Monastery360 backend!")

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('users/', include('users.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)"""


from django.http import HttpResponse

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import FileResponse
import os

# Optional simple home page for backend only
def home(request):
    return HttpResponse("Welcome to Monastery360 backend!")

# View to serve React index.html
def frontend_app(request):
    index_path = os.path.join(settings.BASE_DIR, 'frontend', 'dist', 'index.html')
    return FileResponse(open(index_path, 'rb'))

urlpatterns = [
    path('', home, name='home'),               # optional backend home page
    path('admin/', admin.site.urls),           # Django admin
    path('api/', include('api.urls')),         # API routes
    path('users/', include('users.urls')),     # User auth routes
    re_path(r'^.*$', frontend_app), 
             # catch-all route for React frontend
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
