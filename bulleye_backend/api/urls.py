from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view()),
    path('search/', views.GlobalSearchView.as_view()),
]