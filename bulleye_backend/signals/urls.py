from django.urls import path
from . import views

urlpatterns = [
    path('opportunities/', views.OpportunityRadarView.as_view(), name='opportunities'),
    path('stock/<str:symbol>/', views.StockSignalView.as_view(), name='stock-signal'),
]