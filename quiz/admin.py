from django.contrib import admin
from .models import Category, Quiz, Question, Choice

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ('text', 'quiz')
    search_fields = ['text']

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_premium', 'created_at')
    list_filter = ('category', 'is_premium')

admin.site.register(Category)