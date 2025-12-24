from django.contrib import admin
from django.urls import path, include
from quiz import views as quiz_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Auth (using Allauth)
    path('accounts/', include('allauth.urls')),
    
    # App URLs
    path('', quiz_views.dashboard, name='dashboard'),
    path('quiz/<int:quiz_id>/', quiz_views.take_quiz, name='take_quiz'),
    path('result/<int:attempt_id>/', quiz_views.quiz_result, name='quiz_result'),
]