"""
Make sure the site owner can always log in to /admin/, with the same credentials.

Runs on every boot (start.sh, and the dev compose command) right after
`migrate`. The environment is the source of truth: DJANGO_ADMIN_USERNAME
(default "hesam") and DJANGO_ADMIN_PASSWORD. The user is created if it is
missing; if it exists it is switched back to active, staff and superuser, and
its password is set back to DJANGO_ADMIN_PASSWORD when it differs. So after any
deploy or restart the login is exactly what the .env says. To change the
password, change the .env, not the admin.

There is no default password on purpose: this repository is public. Without
DJANGO_ADMIN_PASSWORD the command fails, and with it the boot, rather than
create an admin anyone could guess.
"""

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

DEFAULT_USERNAME = "hesam"


class Command(BaseCommand):
    help = "Create or repair the admin user from DJANGO_ADMIN_USERNAME / DJANGO_ADMIN_PASSWORD (safe on every boot)."

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_ADMIN_USERNAME") or DEFAULT_USERNAME
        password = os.environ.get("DJANGO_ADMIN_PASSWORD", "")
        if not password:
            raise CommandError(
                "DJANGO_ADMIN_PASSWORD is not set. Put it in .env "
                "(production: printf 'DJANGO_ADMIN_PASSWORD=...\\n' | bash /g/Repos/devops/env-set.sh hesam-ir)."
            )
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
        # Only when it differs: set_password changes the hash, which logs out the admin's sessions.
        if not user.check_password(password):
            user.set_password(password)
            changed.append("password")
        if changed:
            user.save()
            self.stdout.write(self.style.SUCCESS(f"admin: '{username}' restored ({', '.join(changed)})"))
        else:
            self.stdout.write(f"admin: '{username}' exists")
