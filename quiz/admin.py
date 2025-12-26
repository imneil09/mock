from django.contrib import admin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin
from .models import Category, Subject, Question, Choice, Quiz, SubscriptionPlan, UserSubscription

# --- Resource for CSV Import ---
class QuestionResource(resources.ModelResource):
    # This allows importing by Subject Name instead of ID
    subject = fields.Field(
        column_name='subject',
        attribute='subject',
        widget=ForeignKeyWidget(Subject, 'name')
    )

    class Meta:
        model = Question
        fields = ('id', 'subject', 'text', 'explanation', 'difficulty', 'status')
        export_order = ('id', 'subject', 'text', 'explanation')

# --- Inlines ---
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4

# --- Admin Classes ---
@admin.register(Question)
class QuestionAdmin(ImportExportModelAdmin):
    resource_class = QuestionResource
    inlines = [ChoiceInline]
    list_display = ('text', 'subject', 'difficulty', 'status', 'submitted_by', 'created_at')
    list_filter = ('subject', 'status', 'difficulty')
    search_fields = ('text', 'explanation')
    actions = ['approve_questions', 'reject_questions']

    def approve_questions(self, request, queryset):
        queryset.update(status='approved')
    approve_questions.short_description = "Approve selected questions"

    def reject_questions(self, request, queryset):
        queryset.update(status='rejected')

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'is_premium', 'time_limit_minutes', 'created_at')
    list_filter = ('is_premium', 'subject')
    search_fields = ('title',)
    filter_horizontal = ('questions',)  # Widget to select multiple questions easily

# --- Register other models ---
admin.site.register(Category)
admin.site.register(Subject)
admin.site.register(SubscriptionPlan)
admin.site.register(UserSubscription)