"""The Bale bot: a contact message is posted with status buttons, and only the owner can press them.

`bale.call` is patched throughout, so nothing here touches the network.
"""

from unittest import mock

from django.test import TestCase, override_settings
from django.urls import reverse

from apps.content.models import Message
from apps.core import bale

BALE = {"BALE_BOT_TOKEN": "t0ken", "BALE_CHAT_IDS": ["111"], "BALE_WEBHOOK_SECRET": "s3cret"}


@override_settings(GEO_LANGUAGE_ENABLED=False, SITE_URL="https://hesam.ir", **BALE)
class BaleTests(TestCase):
    def setUp(self):
        self.message = Message.objects.create(name="Ali", email="a@example.com", subject="Project", body="Hello")

    def press(self, status, sender=111, pk=None):
        update = {
            "callback_query": {
                "id": "q1",
                "from": {"id": sender},
                "data": f"st:{pk or self.message.pk}:{status}",
                "message": {"message_id": 9, "chat": {"id": sender}},
            }
        }
        with mock.patch.object(bale, "call") as call:
            response = self.client.post(
                reverse("bale_webhook", args=["s3cret"]), data=update, content_type="application/json"
            )
        self.assertEqual(response.status_code, 200)
        return call

    def test_contact_form_notifies(self):
        with mock.patch.object(bale, "notify") as notify:
            self.client.post("/contact/", {"name": "Sara", "email": "s@example.com", "subject": "", "body": "Hi"})
        notify.assert_called_once()
        self.assertEqual(notify.call_args.args[0].name, "Sara")

    def test_spam_is_not_sent(self):
        with mock.patch.object(bale, "notify") as notify:
            self.client.post("/contact/", {"name": "Bot", "email": "b@example.com", "body": "x", "website": "spam"})
        notify.assert_not_called()

    def test_notification_has_details_and_five_buttons(self):
        with mock.patch.object(bale, "call", return_value={}) as call:
            self.assertEqual(bale.notify(self.message, background=False), 1)
        payload = call.call_args.args[1]
        self.assertEqual(payload["chat_id"], "111")
        for part in ("Ali", "a@example.com", "Project", "Hello", "جدید"):
            self.assertIn(part, payload["text"])
        data = [b["callback_data"] for row in payload["reply_markup"]["inline_keyboard"] for b in row if "callback_data" in b]
        self.assertEqual(sorted(d.split(":")[2] for d in data), sorted(Message.Status.values))

    def test_button_changes_status_and_redraws(self):
        call = self.press("starred")
        self.message.refresh_from_db()
        self.assertEqual(self.message.status, Message.Status.STARRED)
        self.assertIsNotNone(self.message.status_changed_at)
        methods = [c.args[0] for c in call.call_args_list]
        self.assertIn("answerCallbackQuery", methods)
        self.assertIn("editMessageText", methods)

    def test_stranger_cannot_change_status(self):
        self.press("rejected", sender=999)
        self.message.refresh_from_db()
        self.assertEqual(self.message.status, Message.Status.NEW)

    def test_wrong_secret_is_404(self):
        response = self.client.post(reverse("bale_webhook", args=["nope"]), data={}, content_type="application/json")
        self.assertEqual(response.status_code, 404)

    @override_settings(BALE_BOT_TOKEN="")
    def test_disabled_sends_nothing(self):
        with mock.patch.object(bale, "call") as call:
            self.assertEqual(bale.notify(self.message, background=False), 0)
        call.assert_not_called()

    def test_long_body_fits_one_message(self):
        self.message.body = "x" * 10000
        self.assertLessEqual(len(bale.render(self.message)), 4096)
