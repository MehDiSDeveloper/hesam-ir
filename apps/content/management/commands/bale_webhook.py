"""Point the Bale bot at this site's webhook — or, with --delete, stop it.

start.sh runs this on every boot, so a changed DJANGO_SITE_URL or a rotated
SECRET_KEY re-registers itself. Without a token, or without an https
DJANGO_SITE_URL (Bale will not call plain http), it says so and does nothing.
"""

from django.conf import settings
from django.core.management.base import BaseCommand
from django.urls import reverse

from apps.core import bale


class Command(BaseCommand):
    help = "Register (or --delete) the Bale bot webhook at DJANGO_SITE_URL."

    def add_arguments(self, parser):
        parser.add_argument("--delete", action="store_true", help="remove the webhook, e.g. before bale_poll")

    def handle(self, *args, delete=False, **options):
        if not settings.BALE_BOT_TOKEN:
            self.stdout.write("bale: BALE_BOT_TOKEN is not set — skipped.")
            return
        if delete:
            ok = bale.call("deleteWebhook") is not None
            self.stdout.write("bale: webhook removed." if ok else "bale: deleteWebhook failed (see log).")
            return
        if not settings.SITE_URL.startswith("https://"):
            self.stdout.write(f"bale: DJANGO_SITE_URL ({settings.SITE_URL}) is not https — use bale_poll instead.")
            return
        url = settings.SITE_URL + reverse("bale_webhook", args=[bale.webhook_secret()])
        ok = bale.call("setWebhook", {"url": url}) is not None
        self.stdout.write(f"bale: webhook set at {settings.SITE_URL}/bale/…" if ok else "bale: setWebhook failed (see log).")
        if not settings.BALE_CHAT_IDS:
            self.stdout.write("bale: BALE_CHAT_IDS is empty — send /id to the bot to learn yours.")
