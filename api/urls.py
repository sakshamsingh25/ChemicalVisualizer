from django.urls import path
from .views import DataSummaryAPI

urlpatterns = [
    # This matches the 'api/summary/' path used in your React App.js
    path('summary/', DataSummaryAPI.as_view(), name='data-summary'),
]