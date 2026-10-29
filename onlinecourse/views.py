from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render

from .models import Choice, Course, Learner, Lesson, Question, Submission


def course_details(request, course_id):
    course = get_object_or_404(
        Course.objects.prefetch_related(
            Prefetch("lessons", queryset=Lesson.objects.prefetch_related("questions__choices"))
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
    submission = Submission.objects.create(learner=learner, course=course)
    valid_choices = Choice.objects.filter(
        question__lesson__course=course,
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
        Submission, pk=submission_id, course=course, learner=learner
    )
    questions = Question.objects.filter(lesson__course=course).prefetch_related(
        "choices", "choices__submissions"
    )

    results = []
    possible_score = 0
    score = 0
    for question in questions:
        correct_choices = list(question.choices.filter(is_correct=True))
        selected_choices = list(submission.choices.filter(question=question))
        is_correct = (
            {choice.id for choice in selected_choices}
            == {choice.id for choice in correct_choices}
            and bool(correct_choices)
        )
        possible_score += question.grade
        if is_correct:
            score += question.grade
        results.append(
            {
                "question": question,
                "selected_choices": selected_choices,
                "correct_choices": correct_choices,
                "is_correct": is_correct,
                "earned_score": question.grade if is_correct else 0,
            }
        )

    percentage = round(score * 100 / possible_score) if possible_score else 0
    submission.grade = percentage
    submission.save(update_fields=["grade"])
    return render(
        request,
        "onlinecourse/exam_result.html",
        {
            "course": course,
            "submission": submission,
            "results": results,
            "score": score,
            "possible_score": possible_score,
            "percentage": percentage,
            "passed": percentage >= 70,
        },
    )