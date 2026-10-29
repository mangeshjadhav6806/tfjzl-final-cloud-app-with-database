from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render

from .models import Choice, Course, Enrollment, Learner, Lesson, Question, Submission


def course_list(request):
    courses = Course.objects.all()
    return render(request, "onlinecourse/course_list.html", {"courses": courses})


def course_details(request, course_id):
    course = get_object_or_404(
        Course.objects.prefetch_related(
            Prefetch("lesson_set", queryset=Lesson.objects.all()),
            "question_set__choices",
        ),
        pk=course_id,
    )
    return render(request, "onlinecourse/course_details_bootstrap.html", {"course": course})
@login_required
def submit(request, course_id):
    if request.method != "POST":
        return redirect("course_details", course_id=course_id)

    course = get_object_or_404(Course, pk=course_id)
    learner = get_object_or_404(Learner, user=request.user)
    enrollment, _ = Enrollment.objects.get_or_create(learner=learner, course=course)
    submission = Submission.objects.create(enrollment=enrollment)
    valid_choices = Choice.objects.filter(
        question__course=course,
        pk__in=request.POST.getlist("choices"),
    )
    submission.choices.set(valid_choices)
    return redirect(
        "show_exam_result", course_id=course.id, submission_id=submission.id
    )


@login_required
def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    learner = get_object_or_404(Learner, user=request.user)
    submission = get_object_or_404(
        Submission,
        pk=submission_id,
        enrollment__course=course,
        enrollment__learner=learner,
    )
    questions = Question.objects.filter(course=course).prefetch_related("choices")

    results = []
    possible = 0
    grade = 0
    selected_ids = list(submission.choices.values_list("id", flat=True))
    for question in questions:
        correct_choices = list(question.choices.filter(is_correct=True))
        selected_choices = list(submission.choices.filter(question=question))
        is_correct = question.is_get_score(choice.id for choice in selected_choices)
        possible += question.grade
        if is_correct:
            grade += question.grade
        results.append(
            {
                "question": question,
                "selected_choices": selected_choices,
                "correct_choices": correct_choices,
                "is_correct": is_correct,
                "earned_score": question.grade if is_correct else 0,
            }
        )

    percentage = round(grade * 100 / possible) if possible else 0
    submission.grade = percentage
    submission.save(update_fields=["grade"])
    return render(
        request,
        "onlinecourse/exam_result_bootstrap.html",
        {
            "course": course,
            "submission": submission,
            "results": results,
            "selected_ids": selected_ids,
            "grade": grade,
            "possible": possible,
            "score": grade,
            "possible_score": possible,
            "percentage": percentage,
            "passed": percentage >= 70,
        },
    )