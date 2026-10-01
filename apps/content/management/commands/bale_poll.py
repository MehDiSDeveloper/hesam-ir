"""Fetch Bale updates by long polling — for a machine Bale cannot reach.

The webhook is the normal route; this is for local work or a host without a
public https address. It removes the webhook first, because Bale answers
getUpdates only while none is set. Run `bale_webhook` again to go back.
"""

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.core import bale


class Command(BaseCommand):
    help = "Long-poll the Bale bot for button presses and commands (Ctrl+C to stop)."

    def handle(self, *args, **options):
        if not settings.BALE_BOT_TOKEN:
            self.stderr.write("BALE_BOT_TOKEN is not set.")
            return
        bale.call("deleteWebhook")
        self.stdout.write("bale: polling… (Ctrl+C to stop)")
        offset = None
        try:
            while True:
                payload = {"timeout": 30} if offset is None else {"timeout": 30, "offset": offset}
                for update in bale.call("getUpdates", payload, timeout=40) or []:
                    offset = update["update_id"] + 1
                    try:
                        bale.handle_update(update)
                    except Exception as exc:  # one bad update must not stop the loop
                        self.stderr.write(f"bale: update {update.get('update_id')} failed: {exc}")
        except KeyboardInterrupt:
            self.stdout.write("bale: stopped.")
