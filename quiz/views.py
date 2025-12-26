from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.contrib import messages
from django.utils import timezone

from quiz.form import QuestionSubmissionForm
from .models import Quiz, QuizAttempt, Question, UserAnswer, Choice, UserSubscription

# Helper to check subscription
def is_premium_member(user):
    return UserSubscription.objects.filter(
        user=user, 
        is_active=True, 
        end_date__gte=timezone.now()
    ).exists()

@login_required
def dashboard(request):
    total_attempts = QuizAttempt.objects.filter(user=request.user).count()
    # Handle case where aggregate returns None
    agg_score = QuizAttempt.objects.filter(user=request.user).aggregate(Sum('score'))['score__sum']
    total_score = agg_score if agg_score else 0
    
    # Show all quizzes, but mark them visually in template if locked
    quizzes = Quiz.objects.all().order_by('-created_at')
    
    context = {
        'total_attempts': total_attempts,
        'total_score': round(total_score, 2),
        'quizzes': quizzes,
        'is_premium': is_premium_member(request.user)
    }
    return render(request, 'dashboard.html', context)

@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # --- SUBSCRIPTION CHECK ---
    if quiz.is_premium and not is_premium_member(request.user):
        messages.error(request, "This is a Premium Quiz. Please upgrade to access.")
        return redirect('dashboard')  # Or redirect to a 'subscribe' page
    # --------------------------

    # Get questions linked to this quiz
    questions = quiz.questions.all().prefetch_related('choices')
    
    if request.method == 'POST':
        return submit_quiz_logic(request, quiz, questions)

    context = {
        'quiz': quiz,
        'questions': questions,
    }
    return render(request, 'take_quiz.html', context)

def submit_quiz_logic(request, quiz, questions):
    # Initialize counters
    correct_count = 0
    wrong_count = 0
    score = 0.0
    
    # Create Attempt
    attempt = QuizAttempt.objects.create(user=request.user, quiz=quiz)

    # Note: Logic assumes Quiz model has fields positive_marks/negative_marks 
    # If not in model, hardcode or add them back to Quiz model (recommended)
    pos_marks = 1.0 
    neg_marks = 0.33

    for question in questions:
        selected_choice_id = request.POST.get(f'q_{question.id}')
        
        selected_choice = None
        if selected_choice_id:
            try:
                selected_choice = Choice.objects.get(id=selected_choice_id)
            except Choice.DoesNotExist:
                pass
        
        # Record Answer
        UserAnswer.objects.create(
            attempt=attempt,
            question=question,
            selected_choice=selected_choice
        )

        # Calculate Score
        if selected_choice:
            if selected_choice.is_correct:
                correct_count += 1
                score += pos_marks
            else:
                wrong_count += 1
                score -= neg_marks
    
    attempt.total_correct = correct_count
    attempt.total_wrong = wrong_count
    attempt.score = score
    attempt.save()

    return redirect('quiz_result', attempt_id=attempt.id)

@login_required
def quiz_result(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    answers = attempt.answers.all().select_related('question', 'selected_choice')
    context = {'attempt': attempt, 'answers': answers}
    return render(request, 'quiz_result.html', context)

@login_required
def submit_question(request):
    if request.method == 'POST':
        form = QuestionSubmissionForm(request.POST)
        if form.is_valid():
            # 1. Save Question (Pending status by default)
            question = form.save(commit=False)
            question.submitted_by = request.user
            question.status = 'pending'
            question.save()

            # 2. Save Choices Manually
            options_data = [
                (form.cleaned_data['option_1'], '1'),
                (form.cleaned_data['option_2'], '2'),
                (form.cleaned_data['option_3'], '3'),
                (form.cleaned_data['option_4'], '4'),
            ]
            
            correct_val = form.cleaned_data['correct_option']
            
            for text, opt_id in options_data:
                Choice.objects.create(
                    question=question,
                    text=text,
                    is_correct=(opt_id == correct_val)
                )

            messages.success(request, "Thank you! Your question has been submitted for approval.")
            return redirect('dashboard')
    else:
        form = QuestionSubmissionForm()

    return render(request, 'submit_question.html', {'form': form})