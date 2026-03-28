from django.db import migrations
from django.contrib.auth.hashers import make_password


DEMO_USER = {
    "username": "demo",
    "email": "demo@bullseye.invest",
    "password": "BullsEye@2024",
    "first_name": "Demo",
    "last_name": "Investor",
    "risk_profile": "moderate",
    "preferred_sectors": ["Technology", "Consumer Discretionary"],
}


def seed_demo_user(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    if not User.objects.filter(username=DEMO_USER["username"]).exists():
        User.objects.create(
            username=DEMO_USER["username"],
            email=DEMO_USER["email"],
            first_name=DEMO_USER["first_name"],
            last_name=DEMO_USER["last_name"],
            password=make_password(DEMO_USER["password"]),
            risk_profile=DEMO_USER["risk_profile"],
            preferred_sectors=DEMO_USER["preferred_sectors"],
            is_staff=False,
            is_superuser=False,
            is_active=True,
        )


def reverse_demo_user(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    User.objects.filter(username=DEMO_USER["username"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_demo_user, reverse_demo_user),
    ]
