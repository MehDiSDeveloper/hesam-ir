from __future__ import annotations

import re

from django import forms
from django.core.exceptions import NON_FIELD_ERRORS

from apps.content.models import Message
from apps.core.i18n import t

# Persian and Arabic-Indic digits → ASCII, so "۰۹۱۲…" typed on a Persian
# keyboard is the same number as "0912…".
_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
# What people put between the digits of a phone number, and nothing else.
_SEPARATORS = re.compile(r"[\s\-‐–—.()/‌‎‏]")


def normalize_phone(raw: str) -> str:
    """Return the number as digits with an optional leading +, or "" if it is not one.

    "00" is the international prefix written out, so it becomes "+". The length
    rule is E.164's (at most 15 digits) with a floor that still admits a local
    landline; anything else in the string — a letter, a second + — rejects it.
    """
    value = _SEPARATORS.sub("", (raw or "").translate(_DIGITS))
    if value.startswith("00"):
        value = "+" + value[2:]
    if not re.fullmatch(r"\+?\d{7,15}", value):
        return ""
    return value


class ContactForm(forms.ModelForm):
    """The contact form, plus a honeypot.

    No captcha: a hidden field a human never sees and a bot fills in stops the
    volume a personal site attracts, and costs the reader nothing.

    Email and phone are each optional and together required: the reader picks
    the way they want to be answered.
    """

    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Message
        fields = ("name", "email", "phone", "subject", "body")
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "name", "maxlength": 120}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "phone": forms.TextInput(attrs={"autocomplete": "tel", "inputmode": "tel"}),
            "subject": forms.TextInput(attrs={"maxlength": 160}),
            "body": forms.Textarea(attrs={"rows": 6, "maxlength": 4000}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # The raw field would cap the input at 20 characters, but "+98 912 345 6789"
        # with its spaces is longer than the number it stores.
        self.fields["phone"].max_length = 32
        self.fields["phone"].validators = []
        self.fields["email"].error_messages["invalid"] = t("contact.email_invalid")

    def clean_phone(self) -> str:
        raw = self.cleaned_data.get("phone", "").strip()
        if not raw:
            return ""
        phone = normalize_phone(raw)
        if not phone:
            raise forms.ValidationError(t("contact.phone_invalid"), code="invalid")
        return phone

    def clean(self):
        cleaned = super().clean()
        # Only when both are empty — a mistyped one already has its own error,
        # and telling the reader to "fill in one" on top of it would be noise.
        if not cleaned.get("email") and not cleaned.get("phone") and not self.has_error("email") and not self.has_error("phone"):
            self.add_error(None, forms.ValidationError(t("contact.reach_required"), code="reach"))
        return cleaned

    @property
    def reach_missing(self) -> bool:
        return self.has_error(NON_FIELD_ERRORS, code="reach")

    def is_spam(self) -> bool:
        return bool(self.data.get("website"))
