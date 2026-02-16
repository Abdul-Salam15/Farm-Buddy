from django.db import models
from django.utils import timezone


class Conversation(models.Model):
    """Represents a chat session"""
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=200, default="New Chat")

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Conversation {self.id}: {self.title}"


class Message(models.Model):
    """Represents a single message in a conversation"""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    image = models.ImageField(upload_to='plant_images/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."
