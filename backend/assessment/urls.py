
# backend/assessment/urls.py
from django.urls import path
from .views import GenerateAssessmentView, ScoreShortAnswersView

urlpatterns = [
    path('generate/', GenerateAssessmentView.as_view(), name='generate-assessment'),
    path('score-short-answers/', ScoreShortAnswersView.as_view(), name='score-short-answers'),
]
