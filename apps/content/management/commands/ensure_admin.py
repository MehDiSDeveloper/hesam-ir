"""
Make sure the site owner can always log in to /admin/.

Runs on every boot (start.sh, and the dev compose command) right after
`migrate`. If the admin user is missing it is created with the default
password; if it exists it is left alone — a password changed in the admin is
kept — except that it is switched back to active, staff and superuser, so it
can never be locked out of the admin by a stray checkbox.

The username and password come from DJANGO_ADMIN_USERNAME and
DJANGO_ADMIN_PASSWORD when set, otherwise from the defaults below.
`--reset-password` puts the password back to that value.
"""

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

DEFAULT_USERNAME = "hesam"
DEFAULT_PASSWORD = "raad505"


class Command(BaseCommand):
    help = "Create the admin user if it does not exist (idempotent, safe on every boot)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset-password",
            action="store_true",
            help="Also set the password back to the configured one if the user already exists.",
        )

    def handle(self, *args, reset_password=False, **options):
        username = os.environ.get("DJANGO_ADMIN_USERNAME") or DEFAULT_USERNAME
        password = os.environ.get("DJANGO_ADMIN_PASSWORD") or DEFAULT_PASSWORD
        User = get_user_model()

        user = User.objects.filter(username=username).first()
        if user is None:
            User.objects.create_superuser(username=username, email="", password=password)
            self.stdout.write(self.style.SUCCESS(f"admin: created '{username}'"))
            return

        changed = []
        for flag in ("is_active", "is_staff", "is_superuser"):
            if not getattr(user, flag):
                setattr(user, flag, True)
                changed.append(flag)
        if reset_password:
            user.set_password(password)
            changed.append("password")
        if changed:
            user.save()
            self.stdout.write(self.style.SUCCESS(f"admin: '{username}' restored ({', '.join(changed)})"))
        else:
            self.stdout.write(f"admin: '{username}' exists")
