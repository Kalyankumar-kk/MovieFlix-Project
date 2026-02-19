from django.urls import path
from . import views

# shared urls for both admin and customer panel
urlpatterns = [
    path('mark_notifications_as_read/', views.mark_notifications_as_read, name='mark_notifications_as_read'),
    path('clear_notifications/', views.clear_notifications, name='clear_notifications'),
    path('delete_single_notification/', views.delete_single_notification, name='delete_single_notification'),
    path('toggle_notifications/', views.toggle_notifications, name='toggle_notifications'),
]