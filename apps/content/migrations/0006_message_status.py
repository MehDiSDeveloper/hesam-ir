from django.db import migrations, models


def handled_to_status(apps, schema_editor):
    # A message already ticked as handled had been read.
    apps.get_model("content", "Message").objects.filter(is_handled=True).update(status="read")


def status_to_handled(apps, schema_editor):
    apps.get_model("content", "Message").objects.exclude(status="new").update(is_handled=True)


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0005_articles"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="status",
            field=models.CharField(
                choices=[("new", "جدید"), ("read", "خوانده شده"), ("rejected", "رد شده"), ("archived", "بایگانی"), ("starred", "محبوب")],
                db_index=True,
                default="new",
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name="message",
            name="status_changed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(handled_to_status, status_to_handled),
        migrations.RemoveField(model_name="message", name="is_handled"),
    ]
