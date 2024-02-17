from django.urls import path

from .views import PermissionsPage, ChatView, PhoneView, AccessTokenPage, SuccessView

urlpatterns = [
    path('permissions', PermissionsPage.as_view(), name="permission-page"),
    path('accesstoken/', AccessTokenPage.as_view(), name="accesstoken-page"),
    path('success/', SuccessView.as_view(), name="success-page"),
    path('chat/', ChatView.as_view(), name='home-chat'),
    path('phone/', PhoneView.as_view(), name='home-phone'),
]