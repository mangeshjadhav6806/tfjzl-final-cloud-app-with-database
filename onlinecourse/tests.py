from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Choice, Course, Enrollment, Learner, Lesson, Question, Submission


class ExamFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="learner", password="test-pass")
        self.learner = Learner.objects.create(user=self.user)
        self.course = Course.objects.create(name="Python Basics")
        self.lesson = Lesson.objects.create(course=self.course, title="Variables")
        self.question = Question.objects.create(
            course=self.course, question_text="Which is a number?", grade=5
        )
        self.correct = Choice.objects.create(
            question=self.question, choice_text="42", is_correct=True
        )
        Choice.objects.create(question=self.question, choice_text="hello")

    def test_submit_and_result_calculates_score(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("submit", args=[self.course.id]), {"choices": [self.correct.id]}
        )

        submission = Submission.objects.get(
            enrollment__learner=self.learner, enrollment__course=self.course
        )
        self.assertRedirects(
            response,
            reverse("show_exam_result", args=[self.course.id, submission.id]),
        )
        result = self.client.get(
            reverse("show_exam_result", args=[self.course.id, submission.id])
        )
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.context["score"], 5)
        self.assertEqual(result.context["possible_score"], 5)
        self.assertEqual(result.context["percentage"], 100)
        self.assertEqual(result.context["grade"], 5)
        self.assertEqual(result.context["possible"], 5)
        self.assertEqual(result.context["selected_ids"], [self.correct.id])
        self.assertContains(result, "Congratulations!")
        self.assertContains(result, "5 / 5")

    def test_submission_string_and_grade_default(self):
        enrollment = Enrollment.objects.create(learner=self.learner, course=self.course)
        submission = Submission.objects.create(enrollment=enrollment)
        self.assertEqual(submission.grade, 0)
        self.assertIn("Python Basics", str(submission))

    def test_question_score_requires_exact_correct_choices(self):
        self.assertTrue(self.question.is_get_score([self.correct.id]))
        self.assertFalse(self.question.is_get_score([]))
        self.assertFalse(self.question.is_get_score([self.correct.id, self.correct.id + 1]))

    def test_course_template_shows_course_and_lessons(self):
        response = self.client.get(reverse("course_details", args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python Basics")
        self.assertContains(response, "Variables")
        self.assertContains(response, "Which is a number?")

    def test_learner_can_sign_in_without_admin_access(self):
        response = self.client.post(
            reverse("login"),
            {"username": "learner", "password": "test-pass"},
        )
        self.assertRedirects(response, reverse("course_list"))