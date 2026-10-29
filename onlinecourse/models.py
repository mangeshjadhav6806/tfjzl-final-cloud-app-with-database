from django.contrib.auth.models import User
from django.db import models


class Instructor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Learner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    courses = models.ManyToManyField("Course", blank=True, related_name="learners")

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Course(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    instructors = models.ManyToManyField(Instructor, blank=True, related_name="courses")

    def __str__(self):
        return self.name


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    sequence = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["sequence", "id"]

    def __str__(self):
        return self.title


class Question(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="questions")
    question_text = models.CharField(max_length=500)
    grade = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    choice_text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text


class Submission(models.Model):
    learner = models.ForeignKey(Learner, on_delete=models.CASCADE, related_name="submissions")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="submissions")
    choices = models.ManyToManyField(Choice, blank=True, related_name="submissions")
    grade = models.PositiveIntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.learner} - {self.course} ({self.grade}%)"