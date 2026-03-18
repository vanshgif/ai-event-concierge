from django.db import models

class EventRequest(models.Model):
    user_input = models.TextField()
    venue_name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    estimated_cost = models.CharField(max_length=100)
    why_it_fits = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)