import django.db.models.deletion
from django.db import migrations, models


def populate_new_relations(apps, schema_editor):
    database = schema_editor.connection.alias
    Enrollment = apps.get_model("onlinecourse", "Enrollment")
    Learner = apps.get_model("onlinecourse", "Learner")
    Question = apps.get_model("onlinecourse", "Question")
    Submission = apps.get_model("onlinecourse", "Submission")

    for question in Question.objects.using(database).select_related("lesson"):
        question.course_id = question.lesson.course_id
        question.save(using=database, update_fields=["course"])

    for learner in Learner.objects.using(database).prefetch_related("courses"):
        for course in learner.courses.all():
            Enrollment.objects.using(database).get_or_create(
                learner_id=learner.pk, course_id=course.pk
            )

    for submission in Submission.objects.using(database).all():
        enrollment, _ = Enrollment.objects.using(database).get_or_create(
            learner_id=submission.learner_id,
            course_id=submission.course_id,
        )
        submission.enrollment_id = enrollment.pk
        submission.save(using=database, update_fields=["enrollment"])


class Migration(migrations.Migration):
    dependencies = [
        ("onlinecourse", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="course",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="onlinecourse.course",
            ),
        ),
        migrations.CreateModel(
            name="Enrollment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date_enrolled", models.DateTimeField(auto_now_add=True)),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="enrollments",
                        to="onlinecourse.course",
                    ),
                ),
                (
                    "learner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="enrollments",
                        to="onlinecourse.learner",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="submission",
            name="enrollment",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="submissions",
                to="onlinecourse.enrollment",
            ),
        ),
        migrations.RunPython(populate_new_relations, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="question",
            name="course",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="onlinecourse.course",
            ),
        ),
        migrations.AlterField(
            model_name="submission",
            name="enrollment",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="submissions",
                to="onlinecourse.enrollment",
            ),
        ),
        migrations.RemoveField(
            model_name="question",
            name="lesson",
        ),
        migrations.RemoveField(
            model_name="learner",
            name="courses",
        ),
        migrations.RemoveField(
            model_name="submission",
            name="course",
        ),
        migrations.RemoveField(
            model_name="submission",
            name="learner",
        ),
    ]