# Generated by Django 4.2.15 on 2025-06-10 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0006_alter_profile_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="image",
            field=models.ImageField(
                blank=True,
                default="defaults/default_profile.png",
                null=True,
                upload_to="profile_images/",
            ),
        ),
        migrations.CreateModel(
            name="ThrottleRecord",
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
                (
                    "ident",
                    models.CharField(
                        help_text="User ID or IP", max_length=255
                    ),
                ),
                (
                    "scope",
                    models.CharField(
                        help_text="Throttle type, e.g., 'changepassword', 'register'",
                        max_length=100,
                    ),
                ),
                ("level", models.PositiveIntegerField(default=0)),
                ("attempts", models.PositiveIntegerField(default=0)),
                ("expires_at", models.DateTimeField()),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-updated_at"],
                "indexes": [
                    models.Index(
                        fields=["ident", "scope"],
                        name="accounts_th_ident_3e2170_idx",
                    )
                ],
                "unique_together": {("ident", "scope")},
            },
        ),
    ]
