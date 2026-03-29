from django.db import models
from accounts.models import User


class ChatQuery(models.Model):
    """
    Stores the history of all AI advisor queries — enables memory and personalization.

    `user` is nullable to support unauthenticated (demo) queries.
    """

    INTENT_CHOICES = [
        ("buy_query", "Buy Query"),
        ("sell_query", "Sell Query"),
        ("portfolio_review", "Portfolio Review"),
        ("market_overview", "Market Overview"),
        ("explain_stock", "Stock Explanation"),
        ("general", "General"),
    ]

    RECOMMENDATION_CHOICES = [
        ("BUY", "Buy"),
        ("HOLD", "Hold"),
        ("AVOID", "Avoid"),
        ("WATCH", "Watch"),
        ("", "None"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="chat_queries"
    )
    query = models.TextField()
    response = models.TextField()

    # New fields for agentic memory
    symbol = models.CharField(max_length=20, blank=True, default="")
    intent = models.CharField(
        max_length=30, choices=INTENT_CHOICES, default="general"
    )
    confidence = models.IntegerField(default=50)
    recommendation = models.CharField(
        max_length=10, choices=RECOMMENDATION_CHOICES, blank=True, default=""
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Chat Query"
        verbose_name_plural = "Chat Queries"
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["symbol"]),
        ]

    def __str__(self):
        user_label = self.user.username if self.user else "anonymous"
        return f"[{self.symbol or 'N/A'}] {user_label}: {self.query[:60]}"