from django import forms
from .models import Question, Subject

class QuestionSubmissionForm(forms.ModelForm):
    # Manually adding fields for choices since they are a separate model
    option_1 = forms.CharField(max_length=200, required=True, label="Option A")
    option_2 = forms.CharField(max_length=200, required=True, label="Option B")
    option_3 = forms.CharField(max_length=200, required=True, label="Option C")
    option_4 = forms.CharField(max_length=200, required=True, label="Option D")
    correct_option = forms.ChoiceField(
        choices=[('1', 'Option A'), ('2', 'Option B'), ('3', 'Option C'), ('4', 'Option D')],
        widget=forms.RadioSelect,
        label="Correct Answer"
    )

    class Meta:
        model = Question
        fields = ['subject', 'text', 'explanation', 'difficulty']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'explanation': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
        }