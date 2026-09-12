import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0036_medication"),
    ]

    operations = [
        migrations.CreateModel(
            name="TimerPurpose",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "purpose",
                    models.CharField(
                        choices=[("breastfeeding", "Breastfeeding")], max_length=32
                    ),
                ),
                (
                    "child",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="core.child"
                    ),
                ),
                (
                    "timer",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="purpose_record",
                        to="core.timer",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="timerpurpose",
            constraint=models.UniqueConstraint(
                fields=("child", "purpose"),
                name="one_breastfeeding_timer_per_child",
            ),
        ),
    ]
