from django.urls import path
from . import views

urlpatterns = [
    # POST /api/ai/chat/ — Main AI advisor chat endpoint
    path("chat/", views.AIAdvisorChatView.as_view(), name="ai-chat"),

    # GET /api/ai/explain/<symbol>/ — Direct stock analysis
    path("explain/<str:symbol>/", views.StockExplainView.as_view(), name="ai-explain"),

    # GET /api/ai/history/ — User's query history
    path("history/", views.ChatHistoryView.as_view(), name="ai-history"),
]