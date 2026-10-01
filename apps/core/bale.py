"""
Contact messages in the Bale messenger (https://bale.ai), with their status
buttons.

Every saved contact message is posted by the bot to the chats listed in
`BALE_CHAT_IDS`, with five buttons under it — new / read / rejected /
archived / starred. Pressing one changes `Message.status` and redraws the
notification, so the whole triage happens in the phone.

The Bot API is Telegram-shaped (`https://tapi.bale.ai/bot<token>/<method>`),
spoken here with the standard library only: one dependency fewer, and the
calls are four small POSTs. Updates arrive at a webhook outside the language
prefix (`/bale/<secret>/`, registered by `manage.py bale_webhook`, which
start.sh runs on boot) or, where there is no public HTTPS address, by
`manage.py bale_poll`.

Only chats in `BALE_CHAT_IDS` may press a button or list messages. Anyone else
who writes to the bot is told their chat id and nothing more — that is how the
owner finds the id to put in the setting.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import threading
import urllib.error
import urllib.request

from django.conf import settings
from django.utils import timezone

from apps.content.models import Message

from .jalali import to_jalali

log = logging.getLogger(__name__)

API = "https://tapi.bale.ai/bot{token}/{method}"
TEXT_LIMIT = 4000  # Bale, like Telegram, stops at 4096 characters

STATUS_ICONS = {
    Message.Status.NEW: "🆕",
    Message.Status.READ: "👁",
    Message.Status.REJECTED: "⛔️",
    Message.Status.ARCHIVED: "🗄",
    Message.Status.STARRED: "⭐️",
}
LANGUAGE_NAMES = {"fa": "فارسی", "en": "انگلیسی", "de": "آلمانی"}


def enabled() -> bool:
    return bool(settings.BALE_BOT_TOKEN and settings.BALE_CHAT_IDS)


def webhook_secret() -> str:
    """The unguessable part of the webhook path, derived so there is no third secret to keep."""
    if settings.BALE_WEBHOOK_SECRET:
        return settings.BALE_WEBHOOK_SECRET
    key = settings.SECRET_KEY.encode()
    return hmac.new(key, f"bale:{settings.BALE_BOT_TOKEN}".encode(), hashlib.sha256).hexdigest()[:40]


def call(method: str, payload: dict | None = None, timeout: float = 10) -> dict | None:
    """One Bot API call. Returns `result`, or None after logging why not."""
    url = API.format(token=settings.BALE_BOT_TOKEN, method=method)
    data = json.dumps(payload or {}, ensure_ascii=False).encode()
    request = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = json.loads(response.read().decode())
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
        log.warning("bale %s failed: %s", method, exc)
        return None
    if not body.get("ok"):
        log.warning("bale %s refused: %s", method, body.get("description"))
        return None
    return body.get("result")


# ── what a notification looks like ─────────────────────────────────────────
def _stamp(value) -> str:
    local = timezone.localtime(value)
    y, m, d = to_jalali(local.date())
    return f"{y}/{m:02d}/{d:02d} — {local:%H:%M}"


def render(message: Message) -> str:
    status = Message.Status(message.status)
    head = [
        f"📩 درخواست همکاری #{message.pk}",
        "",
        f"👤 نام: {message.name}",
    ]
    if message.email:
        head.append(f"✉️ ایمیل: {message.email}")
    if message.phone:
        head.append(f"📞 تلفن: {message.phone}")
    if message.subject:
        head.append(f"📌 موضوع: {message.subject}")
    head += [
        f"🌐 زبان: {LANGUAGE_NAMES.get(message.language, message.language or '—')}",
        f"🕒 زمان: {_stamp(message.created_at)}",
        "",
    ]
    tail = ["", f"وضعیت: {STATUS_ICONS[status]} {status.label}"]
    room = TEXT_LIMIT - len("\n".join(head + tail)) - 2
    body = message.body if len(message.body) <= room else message.body[: room - 1] + "…"
    return "\n".join(head + [body] + tail)


def keyboard(message: Message) -> dict:
    def button(status):
        mark = "✅ " if message.status == status else ""
        return {"text": f"{mark}{STATUS_ICONS[status]} {status.label}", "callback_data": f"st:{message.pk}:{status.value}"}

    s = Message.Status
    rows = [
        [button(s.NEW), button(s.READ), button(s.STARRED)],
        [button(s.REJECTED), button(s.ARCHIVED)],
    ]
    if settings.SITE_URL.startswith("https://"):
        rows.append([{"text": "باز کردن در پنل مدیریت", "url": f"{settings.SITE_URL}/admin/content/message/{message.pk}/change/"}])
    return {"inline_keyboard": rows}


# ── sending ────────────────────────────────────────────────────────────────
def _send(chat_ids, text, markup) -> int:
    return sum(
        call("sendMessage", {"chat_id": chat_id, "text": text, "reply_markup": markup}) is not None
        for chat_id in chat_ids
    )


def notify(message: Message, background: bool = True) -> int:
    """Post a message to every owner chat. In the background, so a slow Bale never slows the form."""
    if not enabled():
        return 0
    # Rendered here, on the request's thread: the worker thread touches no database.
    args = (list(settings.BALE_CHAT_IDS), render(message), keyboard(message))
    if background:
        threading.Thread(target=_send, args=args, daemon=True).start()
        return 0
    return _send(*args)


# ── receiving ──────────────────────────────────────────────────────────────
def _allowed(chat_or_user_id) -> bool:
    return str(chat_or_user_id) in {str(c) for c in settings.BALE_CHAT_IDS}


def handle_update(update: dict) -> None:
    """React to one update from Bale, whichever way it arrived."""
    if "callback_query" in update:
        _handle_button(update["callback_query"])
    elif "message" in update:
        _handle_text(update["message"])


def _handle_button(query: dict) -> None:
    sender = (query.get("from") or {}).get("id")
    chat = ((query.get("message") or {}).get("chat") or {}).get("id")
    if not (_allowed(sender) or _allowed(chat)):
        call("answerCallbackQuery", {"callback_query_id": query.get("id"), "text": "اجازه‌ی این کار را ندارید."})
        return

    try:
        _, pk, value = (query.get("data") or "").split(":")
        status = Message.Status(value)
        message = Message.objects.get(pk=int(pk))
    except (ValueError, Message.DoesNotExist):
        call("answerCallbackQuery", {"callback_query_id": query.get("id"), "text": "این پیام پیدا نشد."})
        return

    if message.status != status:
        message.status = status
        message.status_changed_at = timezone.now()
        message.save(update_fields=["status", "status_changed_at"])
    call("answerCallbackQuery", {"callback_query_id": query.get("id"), "text": f"وضعیت: {status.label}"})

    original = query.get("message") or {}
    if original.get("message_id") and chat is not None:
        call(
            "editMessageText",
            {
                "chat_id": chat,
                "message_id": original["message_id"],
                "text": render(message),
                "reply_markup": keyboard(message),
            },
        )


LIST_COMMANDS = {
    "/new": (Message.Status.NEW, "پیام جدیدی نیست."),
    "/starred": (Message.Status.STARRED, "پیام محبوبی نیست."),
}
HELP = (
    "دستورها:\n"
    "/new — پیام‌های جدید\n"
    "/starred — پیام‌های محبوب\n"
    "/id — شناسه‌ی این گفتگو\n\n"
    "وضعیت هر پیام را با دکمه‌های زیر همان پیام عوض کنید."
)


def _handle_text(incoming: dict) -> None:
    chat = (incoming.get("chat") or {}).get("id")
    if chat is None:
        return
    command = (incoming.get("text") or "").strip().split(maxsplit=1)[0:1]
    command = command[0].split("@")[0].lower() if command else ""

    if not _allowed(chat):
        call(
            "sendMessage",
            {"chat_id": chat, "text": f"شناسه‌ی این گفتگو: {chat}\nبرای دریافت پیام‌ها، آن را در BALE_CHAT_IDS بگذارید."},
        )
        return

    if command == "/id":
        call("sendMessage", {"chat_id": chat, "text": f"شناسه‌ی این گفتگو: {chat}"})
    elif command in LIST_COMMANDS:
        status, empty = LIST_COMMANDS[command]
        found = list(Message.objects.filter(status=status).order_by("created_at")[:20])
        if not found:
            call("sendMessage", {"chat_id": chat, "text": empty})
        for message in found:
            call("sendMessage", {"chat_id": chat, "text": render(message), "reply_markup": keyboard(message)})
    else:
        call("sendMessage", {"chat_id": chat, "text": HELP})
