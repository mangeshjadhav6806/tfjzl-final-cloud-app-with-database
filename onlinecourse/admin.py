from django.contrib import admin

from .models import Choice, Course, Instructor, Learner, Lesson, Question, Submission


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ["question_text", "lesson", "grade"]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ["title", "course", "sequence"]
    list_filter = ["course"]


admin.site.register(Choice)
admin.site.register(Course)
admin.site.register(Instructor)
admin.site.register(Learner)
admin.site.register(Submission)