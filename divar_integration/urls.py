from django.urls import path

from .views import DivarInteractionView, DivarChatNotifierView

urlpatterns = [
    path('', DivarInteractionView.as_view(), name="divar-interaction"),
    path('notifier/', DivarChatNotifierView.as_view(), name="divar-notifier")
]