from django.urls import path
from . import views

urlpatterns = [
    path('stocks/', views.StockListView.as_view()),
    path('stock/<str:symbol>/', views.StockDetailView.as_view()),
    path('filings/', views.FilingsView.as_view()),
]