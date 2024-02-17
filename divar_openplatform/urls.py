"""
URL configuration for divar_openplatform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('home.urls')),
    path('divar/home/', include('divar_homepage.urls')),
    path('divar/oauth/', include('divar_oauth.urls')),
    path('divar/integration/', include('divar_integration.urls')),
    path('admin/', admin.site.urls),
    path('rate/', include('ratino.urls')),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
