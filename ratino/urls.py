from django.urls import path
from .views import RateView, ProfileView

urlpatterns = [
    path('form', RateView.as_view(), name="form"),
    path('profile', ProfileView.as_view(), name="profile"),
]
