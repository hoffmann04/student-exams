from django.contrib import admin

from exam.models import Exam, ExamQuestion, ExamSubmission, Answer

class ExamQuestionInline(admin.TabularInline):
    model = ExamQuestion


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    inlines = [ExamQuestionInline]


class ExamSubmissionAnswerInline(admin.TabularInline):
    model = Answer


@admin.register(ExamSubmission)
class ExamSubmissionAdmin(admin.ModelAdmin):
    inlines = [ExamSubmissionAnswerInline]
