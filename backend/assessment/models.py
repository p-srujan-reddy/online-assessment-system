from django.db import models
from django.contrib.auth.models import User

class Assessment(models.Model):
    ASSESSMENT_TYPES = (
        ('mcq', 'Multiple Choice'),
        ('short_answer', 'Short Answer'),
    )

    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_assessments')
    title = models.CharField(max_length=200)
    topic = models.CharField(max_length=200)
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES)
    question_count = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    max_score = models.FloatField(default=1.0)

    def __str__(self):
        return f"Question for {self.assessment.title}"

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.TextField()
    is_correct = models.BooleanField(default=False)  # For MCQ

    def __str__(self):
        return f"Answer for {self.question}"
    
class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name