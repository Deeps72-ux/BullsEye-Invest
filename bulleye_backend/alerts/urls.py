from django.urls import path
from . import views

urlpatterns = [
    path('', views.AlertListView.as_view()),
    path('subscribe/', views.SubscribeAlertView.as_view()),
    path('<int:alert_id>/read/', views.MarkAlertReadView.as_view()),
    path('read-all/', views.MarkAllAlertsReadView.as_view()),
]