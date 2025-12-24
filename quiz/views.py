from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Quiz, QuizAttempt, Question, UserAnswer, Choice
from django.db.models import Sum

@login_required
def dashboard(request):
    """
    Renders the Student Dashboard with stats.
    """
    # Simple stats calculation
    total_attempts = QuizAttempt.objects.filter(user=request.user).count()
    total_score = QuizAttempt.objects.filter(user=request.user).aggregate(Sum('score'))['score__sum'] or 0
    
    # Get available quizzes
    active_quizzes = Quiz.objects.filter(is_premium=False) # Or handle premium logic
    
    context = {
        'total_attempts': total_attempts,
        'total_score': round(total_score, 2),
        'active_quizzes': active_quizzes
    }
    return render(request, 'dashboard.html', context)

@login_required
def take_quiz(request, quiz_id):
    """
    Loads the exam interface.
    """
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all().prefetch_related('choices').order_by('order')
    
    if request.method == 'POST':
        # Logic to handle submission (HTMX or Standard Form)
        return submit_quiz(request, quiz, questions)

    context = {
        'quiz': quiz,
        'questions': questions,
    }
    return render(request, 'take_quiz.html', context)

def submit_quiz(request, quiz, questions):
    """
    Calculates score and saves the attempt.
    """
    correct_count = 0
    wrong_count = 0
    score = 0.0

    attempt = QuizAttempt.objects.create(user=request.user, quiz=quiz)

    for question in questions:
        selected_choice_id = request.POST.get(f'q_{question.id}')
        
        if selected_choice_id:
            selected_choice = Choice.objects.get(id=selected_choice_id)
            UserAnswer.objects.create(
                attempt=attempt,
                question=question,
                selected_choice=selected_choice
            )

            if selected_choice.is_correct:
                correct_count += 1
                score += quiz.positive_marks
            else:
                wrong_count += 1
                score -= quiz.negative_marks
        else:
            # Skipped question
            UserAnswer.objects.create(
                attempt=attempt,
                question=question,
                selected_choice=None
            )

    # Update attempt with final calculation
    attempt.total_correct = correct_count
    attempt.total_wrong = wrong_count
    attempt.score = score
    attempt.save()

    return redirect('quiz_result', attempt_id=attempt.id)

@login_required
def quiz_result(request, attempt_id):
    """
    Renders the Analytics/Result page.
    """
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    answers = attempt.answers.all().select_related('question', 'selected_choice')
    
    context = {
        'attempt': attempt,
        'answers': answers,
    }
    return render(request, 'quiz_result.html', context)