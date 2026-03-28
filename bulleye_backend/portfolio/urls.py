from django.urls import path
from . import views

urlpatterns = [
    path('', views.PortfolioView.as_view()),
    path('holdings/', views.HoldingsView.as_view()),
    path('analysis/', views.PortfolioAnalysisView.as_view()),
]