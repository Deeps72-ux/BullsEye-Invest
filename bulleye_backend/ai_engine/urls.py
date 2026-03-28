from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.MarketChatView.as_view()),
    path('explain/<str:symbol>/', views.StockExplainView.as_view()),
]