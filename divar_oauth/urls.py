from django.urls import path

from .views import OAuthView

urlpatterns = [
    path('', OAuthView.as_view(), name="divar-oauth"),
]