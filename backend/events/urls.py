from django.urls import path
from .views import generate_event, get_history

urlpatterns = [
path('generate/', generate_event),
path('history/', get_history),
]