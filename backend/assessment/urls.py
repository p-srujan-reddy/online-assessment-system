
# backend/assessment/urls.py

from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
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
    path('upload-document/', FileUploadView.as_view(), name='upload-document'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
