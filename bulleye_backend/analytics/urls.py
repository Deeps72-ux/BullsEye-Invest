from django.urls import path
from . import views

urlpatterns = [
    path('patterns/<str:symbol>/', views.PatternDetectionView.as_view()),
    path('indicators/<str:symbol>/', views.IndicatorView.as_view()),
    path('backtest/<str:symbol>/', views.BacktestView.as_view()),
]