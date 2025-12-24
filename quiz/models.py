from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100) # e.g., "Indian Polity", "Tripura GK"
    slug = models.SlugField(unique=True)
    
    def __str__(self):
        return self.name

class Quiz(models.Model):
    title = models.CharField(max_length=200) # e.g., "TPSC Combined Mock #4"
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    total_questions = models.IntegerField(default=100)
    time_limit_minutes = models.IntegerField(default=120)
    positive_marks = models.FloatField(default=1.0)
    negative_marks = models.FloatField(default=0.33)
    is_premium = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    text = models.TextField()
    explanation = models.TextField(help_text="Shown after the user submits the quiz")
    order = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.text[:50]}..."

class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    label = models.CharField(max_length=1, choices=[('A','A'), ('B','B'), ('C','C'), ('D','D')])

    def __str__(self):
        return f"({self.label}) {self.text}"

class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.FloatField(default=0.0)
    total_correct = models.IntegerField(default=0)
    total_wrong = models.IntegerField(default=0)
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} - {self.score}"

class UserAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, null=True, blank=True, on_delete=models.SET_NULL)