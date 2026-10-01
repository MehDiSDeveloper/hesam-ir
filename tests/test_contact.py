"""The contact form: email or phone, at least one — and the honeypot and throttle still refuse.

`bale.notify` is patched throughout, so nothing here touches the network.
"""

from unittest import mock

from django.db import IntegrityError
from django.test import TestCase, override_settings

from apps.content.models import Message
from apps.core import bale
from apps.core.forms import normalize_phone


@override_settings(GEO_LANGUAGE_ENABLED=False, SITE_URL="https://hesam.ir")
class ContactFormTests(TestCase):
    def post(self, url="/contact/", **fields):
        data = {"name": "Sara", "email": "", "phone": "", "subject": "", "body": "Hi"} | fields
        with mock.patch.object(bale, "notify"):
            return self.client.post(url, data)

    def test_email_alone_is_enough(self):
        self.assertRedirects(self.post(email="s@example.com"), "/contact/?sent=1")
        self.assertEqual(Message.objects.get().phone, "")

    def test_phone_alone_is_enough_and_is_normalised(self):
        self.assertRedirects(self.post(phone="۰۹۱۲ ۳۴۵-۶۷۸۹"), "/contact/?sent=1")
        message = Message.objects.get()
        self.assertEqual((message.email, message.phone), ("", "09123456789"))

    def test_both_are_kept(self):
        self.post(email="s@example.com", phone="0049 151 2345678")
        message = Message.objects.get()
        self.assertEqual((message.email, message.phone), ("s@example.com", "+491512345678"))

    def test_neither_is_refused_with_one_message_in_the_readers_language(self):
        response = self.post(url="/en/contact/")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Message.objects.exists())
        self.assertTrue(response.context["form"].reach_missing)
        self.assertContains(response, "Leave one way to reply", count=1)
        # The constraint is the database's backstop; its own generic error must not show too.
        self.assertNotContains(response, "message_has_reply_channel")
        self.assertContains(response, 'class="reach is-invalid"')

    def test_a_bad_phone_says_so_and_nothing_else(self):
        response = self.post(phone="call me")
        self.assertFalse(Message.objects.exists())
        form = response.context["form"]
        self.assertTrue(form.has_error("phone"))
        self.assertFalse(form.reach_missing)
        self.assertContains(response, 'id="id_phone"')
        self.assertContains(response, 'aria-invalid="true" aria-describedby="err_phone"')

    def test_a_bad_email_is_refused_even_with_a_good_phone(self):
        self.post(email="not-an-email", phone="09123456789")
        self.assertFalse(Message.objects.exists())

    def test_honeypot_and_throttle_refuse_without_saving(self):
        self.assertRedirects(self.post(email="b@example.com", website="spam"), "/contact/?sent=1")
        self.assertFalse(Message.objects.exists())
        self.post(email="s@example.com")
        response = self.post(email="s@example.com")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Message.objects.count(), 1)

    def test_database_refuses_a_message_with_no_way_to_reply(self):
        with self.assertRaises(IntegrityError):
            Message.objects.create(name="X", body="y")

    def test_notification_shows_only_the_channels_given(self):
        message = Message.objects.create(name="Ali", phone="09123456789", body="Hello")
        text = bale.render(message)
        self.assertIn("09123456789", text)
        self.assertNotIn("ایمیل", text)


class NormalizePhoneTests(TestCase):
    def test_accepts_the_ways_people_write_numbers(self):
        cases = {
            "09123456789": "09123456789",
            "۰۹۱۲ ۳۴۵ ۶۷۸۹": "09123456789",
            "٠٩١٢٣٤٥٦٧٨٩": "09123456789",
            "+98 (912) 345-6789": "+989123456789",
            "0098 912 345 6789": "+989123456789",
            "+49 151.2345678": "+491512345678",
        }
        for raw, expected in cases.items():
            self.assertEqual(normalize_phone(raw), expected, raw)

    def test_refuses_what_is_not_a_number(self):
        for raw in ("", "abc", "12345", "+", "0912345678901234567", "09123x456789", "++989123456789"):
            self.assertEqual(normalize_phone(raw), "", raw)
