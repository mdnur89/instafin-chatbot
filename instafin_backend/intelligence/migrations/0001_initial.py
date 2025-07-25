# Generated by Django 5.1.5 on 2025-01-21 06:31

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="NLUModel",
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
                ("name", models.CharField(max_length=100, unique=True)),
                ("description", models.TextField()),
                (
                    "model_type",
                    models.CharField(
                        choices=[
                            ("intent", "Intent Classification"),
                            ("entity", "Entity Recognition"),
                            ("sentiment", "Sentiment Analysis"),
                            ("combined", "Combined Model"),
                        ],
                        max_length=50,
                    ),
                ),
                ("version", models.CharField(max_length=20)),
                (
                    "configuration",
                    models.JSONField(
                        help_text="Model-specific configuration parameters"
                    ),
                ),
                ("performance_metrics", models.JSONField(blank=True, default=dict)),
                ("is_active", models.BooleanField(default=True)),
                ("is_training", models.BooleanField(default=False)),
                ("last_trained", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Category",
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
                ("name", models.CharField(max_length=100, unique=True)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="intelligence.category",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Categories",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="FAQ",
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
                ("question", models.TextField()),
                ("answer", models.TextField()),
                (
                    "variations",
                    models.JSONField(
                        default=list, help_text="Alternative phrasings of the question"
                    ),
                ),
                (
                    "priority",
                    models.IntegerField(
                        default=1,
                        help_text="1-10 scale, higher number means higher priority",
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(10),
                        ],
                    ),
                ),
                (
                    "is_training_data",
                    models.BooleanField(
                        default=True, help_text="Use this FAQ for training NLU models"
                    ),
                ),
                (
                    "is_public",
                    models.BooleanField(
                        default=True, help_text="Show this FAQ to users"
                    ),
                ),
                (
                    "usage_count",
                    models.IntegerField(
                        default=0, help_text="Number of times this FAQ was used"
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="intelligence.category",
                    ),
                ),
            ],
            options={
                "verbose_name": "FAQ",
                "verbose_name_plural": "FAQs",
                "ordering": ["-priority", "-usage_count"],
            },
        ),
        migrations.CreateModel(
            name="TrainingSession",
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
                ("start_time", models.DateTimeField(auto_now_add=True)),
                ("end_time", models.DateTimeField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("running", "Running"),
                            ("completed", "Completed"),
                            ("failed", "Failed"),
                        ],
                        max_length=20,
                    ),
                ),
                ("metrics", models.JSONField(blank=True, default=dict)),
                ("error_log", models.TextField(blank=True)),
                (
                    "model",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="intelligence.nlumodel",
                    ),
                ),
            ],
        ),
    ]
