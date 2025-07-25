# Generated by Django 5.1.5 on 2025-02-10 14:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chat_platform", "0001_initial"),
        ("communications", "0007_chatsession_platform"),
    ]

    operations = [
        migrations.CreateModel(
            name="PlatformMessage",
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
                ("external_id", models.CharField(max_length=255)),
                (
                    "direction",
                    models.CharField(
                        choices=[("in", "Incoming"), ("out", "Outgoing")], max_length=10
                    ),
                ),
                ("content", models.JSONField()),
                ("metadata", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "chat_session",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="platform_messages",
                        to="communications.chatsession",
                    ),
                ),
                (
                    "platform",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="chat_platform.chatplatform",
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(
                        fields=["external_id"], name="chat_platfo_externa_8a42c5_idx"
                    ),
                    models.Index(
                        fields=["chat_session", "created_at"],
                        name="chat_platfo_chat_se_864c19_idx",
                    ),
                ],
            },
        ),
    ]
