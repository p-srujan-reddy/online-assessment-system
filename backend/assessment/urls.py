
# backend/assessment/urls.py

from django.urls import path
from .views import (
    GenerateAssessmentView, 
    ScoreShortAnswersView, 
    ScoreLongAnswersView, 
    ScoreFillInTheBlanksView, 
)

urlpatterns = [
    path('generate/', GenerateAssessmentView.as_view(), name='generate-assessment'),
    path('score-short-answers/', ScoreShortAnswersView.as_view(), name='score-short-answers'),
    path('score-long-answers/', ScoreLongAnswersView.as_view(), name='score-long-answers'),
    path('score-fill-in-the-blanks/', ScoreFillInTheBlanksView.as_view(), name='score-fill-in-the-blanks'),
]
