
# backend/assessment/urls.py
from django.urls import path
from .views import GenerateAssessmentView

urlpatterns = [
    path('generate/', GenerateAssessmentView.as_view(), name='generate-assessment'),  # Ensure this path matches
]
