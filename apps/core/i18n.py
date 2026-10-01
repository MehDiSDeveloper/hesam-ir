"""
UI strings, in the three languages, as one Python dict.

Why not Django's gettext catalogues: those need .po files compiled by the
`msgfmt` binary, which turns "add a word to a button" into a build step that
has to run on Windows, in CI and inside the image. This site's UI vocabulary is
about a hundred short strings that only ever change when a feature changes, so
a dict costs one import and no toolchain, and an agent can add a language by
adding a column here.

Everything a *visitor* reads that is not chrome — a project title, a post, a
bio — lives in the database instead (see apps/content/models.py). This file is
only the furniture: buttons, labels, section headings.

Read it from a template with {% t "nav.projects" %}.
"""

from __future__ import annotations

from django.conf import settings
from django.utils.translation import get_language

DEFAULT_LANG = settings.LANGUAGE_CODE

STRINGS: dict[str, dict[str, str]] = {
    # ── chrome ────────────────────────────────────────────────────────────
    "nav.home": {"fa": "خانه", "en": "Home", "de": "Start"},
    "nav.projects": {"fa": "پروژه‌ها", "en": "Work", "de": "Projekte"},
    "nav.writing": {"fa": "نوشته‌ها", "en": "Writing", "de": "Blog"},
    "nav.articles": {"fa": "مقالات", "en": "Articles", "de": "Artikel"},
    "nav.about": {"fa": "درباره", "en": "About", "de": "Über mich"},
    "nav.contact": {"fa": "تماس", "en": "Contact", "de": "Kontakt"},
    "nav.resume": {"fa": "رزومه", "en": "Resume", "de": "Lebenslauf"},
    "nav.card": {"fa": "کارت", "en": "Card", "de": "Karte"},
    "nav.menu": {"fa": "منو", "en": "Menu", "de": "Menü"},
    "nav.close": {"fa": "بستن", "en": "Close", "de": "Schließen"},
    "nav.skip": {"fa": "پرش به محتوا", "en": "Skip to content", "de": "Zum Inhalt springen"},
    "nav.language": {"fa": "زبان", "en": "Language", "de": "Sprache"},
    "nav.theme": {"fa": "تم", "en": "Theme", "de": "Design"},
    "theme.system": {"fa": "سیستم", "en": "System", "de": "System"},
    "theme.light": {"fa": "روشن", "en": "Light", "de": "Hell"},
    "theme.dark": {"fa": "تاریک", "en": "Dark", "de": "Dunkel"},

    # ── home ──────────────────────────────────────────────────────────────
    "home.available": {"fa": "آمادهٔ همکاری", "en": "Open to work", "de": "Offen für Projekte"},
    "home.view_work": {"fa": "دیدن پروژه‌ها", "en": "See my work", "de": "Projekte ansehen"},
    "home.contact_me": {"fa": "تماس با من", "en": "Get in touch", "de": "Kontakt aufnehmen"},
    "home.download_resume": {"fa": "دانلود رزومه", "en": "Download résumé", "de": "Lebenslauf laden"},
    "home.now": {"fa": "این روزها", "en": "Right now", "de": "Gerade jetzt"},
    "home.selected_work": {"fa": "کارهای منتخب", "en": "Selected work", "de": "Ausgewählte Projekte"},
    "home.all_projects": {"fa": "همهٔ پروژه‌ها", "en": "All projects", "de": "Alle Projekte"},
    "home.skills": {"fa": "چیزهایی که با آن‌ها کار می‌کنم", "en": "What I work with", "de": "Womit ich arbeite"},
    "home.experience": {"fa": "مسیر کاری", "en": "Career", "de": "Werdegang"},
    "home.full_resume": {"fa": "رزومهٔ کامل", "en": "Full résumé", "de": "Ganzer Lebenslauf"},
    "home.writing": {"fa": "نوشته‌ها", "en": "Writing", "de": "Aus dem Blog"},
    "home.all_writing": {"fa": "همهٔ نوشته‌ها", "en": "All posts", "de": "Alle Beiträge"},
    "home.cta_title": {"fa": "پروژه‌ای در ذهن دارید؟", "en": "Have something in mind?", "de": "Sie haben eine Idee?"},
    "home.cta_body": {
        "fa": "برای برنامه‌ریزی و کنترل یک پروژه‌ی عمرانی، تحلیل تأخیرات، پیشنهاد همکاری یا فقط یک گفت‌وگوی تخصصی، پیام بدهید.",
        "en": "For planning and controlling a construction project, a delay analysis, a role, or just a professional conversation — send a message.",
        "de": "Für Planung und Steuerung eines Bauprojekts, eine Verzugsanalyse, eine Stelle oder einfach ein Fachgespräch — schreiben Sie mir.",
    },

    # ── services ──────────────────────────────────────────────────────────
    "nav.services": {"fa": "خدمات", "en": "Services", "de": "Leistungen"},
    "services.start": {"fa": "ثبت درخواست پروژه", "en": "Start a project", "de": "Projekt anfragen"},
    "services.more": {"fa": "جزئیات همکاری", "en": "How it works", "de": "So läuft es ab"},
    "services.subject": {"fa": "درخواست انجام پروژه", "en": "Project enquiry", "de": "Projektanfrage"},
    "services.cta_title": {"fa": "پروژه‌تان را شروع کنیم؟", "en": "Shall we start your project?", "de": "Starten wir Ihr Projekt?"},
    "services.cta_body": {
        "fa": "چند خط درباره‌ی پروژه، وضعیت فعلی برنامه و آنچه لازم دارید بنویسید.",
        "en": "Write a few lines about the project, where its programme stands and what you need.",
        "de": "Schreiben Sie ein paar Zeilen zum Projekt, zum Stand des Terminplans und zu Ihrem Bedarf.",
    },

    # ── projects ──────────────────────────────────────────────────────────
    "projects.title": {"fa": "پروژه‌ها", "en": "Work", "de": "Projekte"},
    "projects.lede": {
        "fa": "حوزه‌های کاری‌ام، و روشی که هر کدام را با آن پیش می‌برم.",
        "en": "The areas I work in, and the method behind each one.",
        "de": "Meine Arbeitsfelder — und die Methode hinter jedem.",
    },
    "projects.filter_all": {"fa": "همه", "en": "All", "de": "Alle"},
    "projects.empty": {"fa": "چیزی با این فیلتر پیدا نشد.", "en": "Nothing matches this filter.", "de": "Nichts gefunden."},
    "projects.role": {"fa": "نقش", "en": "Role", "de": "Rolle"},
    "projects.year": {"fa": "سال", "en": "Year", "de": "Jahr"},
    "projects.stack": {"fa": "ابزار و روش", "en": "Tools & methods", "de": "Werkzeuge & Methoden"},
    "projects.problem": {"fa": "مسئله", "en": "The problem", "de": "Das Problem"},
    "projects.outcome": {"fa": "نتیجه", "en": "Outcome", "de": "Ergebnis"},
    "projects.repo": {"fa": "مخزن کد", "en": "Source", "de": "Quellcode"},
    "projects.demo": {"fa": "نسخهٔ زنده", "en": "Live demo", "de": "Live-Demo"},
    "projects.next": {"fa": "پروژهٔ بعدی", "en": "Next project", "de": "Nächstes Projekt"},
    "projects.back": {"fa": "بازگشت به پروژه‌ها", "en": "Back to work", "de": "Zurück zu den Projekten"},

    # ── writing ───────────────────────────────────────────────────────────
    "blog.title": {"fa": "نوشته‌ها", "en": "Writing", "de": "Blog"},
    "blog.lede": {
        "fa": "یادداشت‌هایی دربارهٔ چیزهایی که یاد می‌گیرم، مسائلی که درگیرشان هستم و گاهی فقط یک فکر.",
        "en": "Notes on what I am learning, problems I am chewing on, and the occasional thought.",
        "de": "Notizen über das, was ich lerne, Probleme, an denen ich sitze — und gelegentlich ein Gedanke.",
    },
    "blog.read_time": {"fa": "دقیقه مطالعه", "en": "min read", "de": "Min. Lesezeit"},
    "blog.back": {"fa": "بازگشت به نوشته‌ها", "en": "Back to writing", "de": "Zurück zum Blog"},
    "blog.empty": {"fa": "هنوز چیزی منتشر نشده.", "en": "Nothing published yet.", "de": "Noch nichts veröffentlicht."},
    "blog.share": {"fa": "اشتراک‌گذاری", "en": "Share", "de": "Teilen"},
    "blog.related": {"fa": "نوشته‌های دیگر", "en": "More writing", "de": "Weitere Beiträge"},
    "blog.only_in": {
        "fa": "این نوشته فقط به این زبان منتشر شده:",
        "en": "This post is only available in:",
        "de": "Dieser Beitrag ist nur verfügbar in:",
    },
    "blog.original_on": {"fa": "نسخه‌ی اصلی این نوشته در", "en": "Originally posted on", "de": "Ursprünglich veröffentlicht auf"},
    "blog.original_open": {"fa": "دیدن پست اصلی", "en": "Open the original", "de": "Original öffnen"},
    "platform.linkedin": {"fa": "لینکدین", "en": "LinkedIn", "de": "LinkedIn"},
    "platform.x": {"fa": "ایکس", "en": "X", "de": "X"},
    "platform.github": {"fa": "گیت‌هاب", "en": "GitHub", "de": "GitHub"},
    "platform.telegram": {"fa": "تلگرام", "en": "Telegram", "de": "Telegram"},
    "platform.medium": {"fa": "مدیوم", "en": "Medium", "de": "Medium"},
    "platform.virgool": {"fa": "ویرگول", "en": "Virgool", "de": "Virgool"},
    "platform.devto": {"fa": "DEV", "en": "DEV", "de": "DEV"},
    "platform.web": {"fa": "سایت دیگری", "en": "another site", "de": "einer anderen Website"},

    # ── articles ──────────────────────────────────────────────────────────
    "articles.title": {"fa": "مقالات", "en": "Articles", "de": "Artikel"},
    "articles.lede": {
        "fa": "مقاله‌های تخصصی و پژوهشی در برنامه‌ریزی، کنترل پروژه و تحلیل تأخیرات.",
        "en": "Professional and research articles on planning, project control and delay analysis.",
        "de": "Fach- und Forschungsartikel zu Terminplanung, Projektsteuerung und Verzugsanalyse.",
    },
    "articles.abstract": {"fa": "چکیده", "en": "Abstract", "de": "Zusammenfassung"},
    "articles.authors": {"fa": "نویسندگان", "en": "Authors", "de": "Autoren"},
    "articles.venue": {"fa": "محل انتشار", "en": "Published in", "de": "Erschienen in"},
    "articles.pdf": {"fa": "دانلود PDF", "en": "Download PDF", "de": "PDF laden"},
    "articles.external": {"fa": "مشاهده در محل انتشار", "en": "View at the publisher", "de": "Beim Verlag ansehen"},
    "articles.back": {"fa": "بازگشت به مقالات", "en": "Back to articles", "de": "Zurück zu den Artikeln"},
    "articles.all": {"fa": "همهٔ مقالات", "en": "All articles", "de": "Alle Artikel"},
    "articles.empty": {"fa": "هنوز مقاله‌ای منتشر نشده.", "en": "No articles published yet.", "de": "Noch keine Artikel veröffentlicht."},
    "articles.related": {"fa": "مقاله‌های دیگر", "en": "More articles", "de": "Weitere Artikel"},
    "articles.only_in": {
        "fa": "این مقاله فقط به این زبان منتشر شده:",
        "en": "This article is only available in:",
        "de": "Dieser Artikel ist nur verfügbar in:",
    },

    # ── about ─────────────────────────────────────────────────────────────
    "about.title": {"fa": "درباره من", "en": "About", "de": "Über mich"},
    "about.work": {"fa": "سابقهٔ کاری", "en": "Experience", "de": "Berufserfahrung"},
    "about.education": {"fa": "تحصیلات", "en": "Education", "de": "Ausbildung"},
    "about.present": {"fa": "اکنون", "en": "Present", "de": "Heute"},

    # ── contact ───────────────────────────────────────────────────────────
    "contact.title": {"fa": "تماس", "en": "Contact", "de": "Kontakt"},
    "contact.lede": {
        "fa": "هر کدام از راه‌های زیر جواب می‌دهد. برای پیام بلندتر، فرم پایین سریع‌ترین راه است.",
        "en": "Any of these reaches me. For anything longer, the form below is quickest.",
        "de": "Jeder dieser Wege erreicht mich. Für Längeres ist das Formular am schnellsten.",
    },
    "contact.direct": {"fa": "راه‌های مستقیم", "en": "Direct channels", "de": "Direkte Wege"},
    "contact.form": {"fa": "پیام بفرستید", "en": "Send a message", "de": "Nachricht senden"},
    "contact.name": {"fa": "نام", "en": "Name", "de": "Name"},
    "contact.email": {"fa": "ایمیل", "en": "Email", "de": "E-Mail"},
    "contact.phone": {"fa": "شماره موبایل", "en": "Phone", "de": "Telefon"},
    "contact.phone_ph": {"fa": "0912 345 6789", "en": "+1 555 123 4567", "de": "+49 151 2345678"},
    "contact.reach": {"fa": "چطور جوابتان را بدهم؟", "en": "How should I reply?", "de": "Wie darf ich antworten?"},
    "contact.reach_hint": {
        "fa": "ایمیل یا شماره موبایل — یکی کافی است، هر دو بهتر.",
        "en": "Email or phone — one is enough, both is better.",
        "de": "E-Mail oder Telefon — eines genügt, beides ist besser.",
    },
    "contact.reach_required": {
        "fa": "یک راه برای جواب بگذارید: ایمیل یا شماره موبایل.",
        "en": "Leave one way to reply: an email or a phone number.",
        "de": "Bitte einen Weg für die Antwort angeben: E-Mail oder Telefon.",
    },
    "contact.email_invalid": {
        "fa": "این ایمیل درست به نظر نمی‌رسد — مثل name@example.com",
        "en": "This email does not look right — e.g. name@example.com",
        "de": "Diese E-Mail sieht nicht richtig aus — z. B. name@example.com",
    },
    "contact.phone_invalid": {
        "fa": "این شماره درست به نظر نمی‌رسد — مثل 09123456789 یا با کد کشور.",
        "en": "This number does not look right — include the country code, e.g. +44 7700 900123.",
        "de": "Diese Nummer sieht nicht richtig aus — mit Ländervorwahl, z. B. +49 151 2345678.",
    },
    "contact.optional": {"fa": "اختیاری", "en": "optional", "de": "optional"},
    "contact.subject": {"fa": "موضوع", "en": "Subject", "de": "Betreff"},
    "contact.message": {"fa": "پیام", "en": "Message", "de": "Nachricht"},
    "contact.send": {"fa": "ارسال پیام", "en": "Send message", "de": "Absenden"},
    "contact.sent": {
        "fa": "پیام شما رسید. به‌زودی جواب می‌دهم.",
        "en": "Your message arrived. I will get back to you shortly.",
        "de": "Ihre Nachricht ist angekommen. Ich melde mich in Kürze.",
    },
    "contact.too_fast": {
        "fa": "یک پیام همین الان فرستادید. کمی صبر کنید.",
        "en": "You just sent one. Give it a minute.",
        "de": "Sie haben gerade eine gesendet. Einen Moment bitte.",
    },
    "contact.copy": {"fa": "کپی", "en": "Copy", "de": "Kopieren"},
    "contact.copied": {"fa": "کپی شد", "en": "Copied", "de": "Kopiert"},

    # ── card ──────────────────────────────────────────────────────────────
    "card.title": {"fa": "کارت ویزیت", "en": "Business card", "de": "Visitenkarte"},
    "card.add_contact": {"fa": "افزودن به مخاطبین", "en": "Add to contacts", "de": "Zu Kontakten"},
    "card.scan": {"fa": "این کد را اسکن کنید", "en": "Scan this code", "de": "Diesen Code scannen"},
    "card.share": {"fa": "اشتراک‌گذاری لینک", "en": "Share link", "de": "Link teilen"},
    "card.open_site": {"fa": "دیدن سایت کامل", "en": "Open full site", "de": "Ganze Website"},

    # ── resume ────────────────────────────────────────────────────────────
    "resume.title": {"fa": "رزومه", "en": "Resume", "de": "Lebenslauf"},
    "resume.print": {"fa": "چاپ / PDF", "en": "Print / PDF", "de": "Drucken / PDF"},
    "resume.languages": {"fa": "زبان‌ها", "en": "Languages", "de": "Sprachen"},

    # ── errors and footer ─────────────────────────────────────────────────
    "err.404_title": {"fa": "این صفحه پیدا نشد", "en": "Page not found", "de": "Seite nicht gefunden"},
    "err.404_body": {
        "fa": "شاید نشانی عوض شده باشد. از خانه دوباره شروع کنید.",
        "en": "The address may have changed. Start again from the home page.",
        "de": "Die Adresse hat sich vielleicht geändert. Beginnen Sie auf der Startseite.",
    },
    "err.500_title": {"fa": "چیزی از سمت ما خراب شد", "en": "Something broke on our side", "de": "Auf unserer Seite ging etwas schief"},
    "err.500_body": {
        "fa": "خطا ثبت شد. کمی بعد دوباره تلاش کنید.",
        "en": "The error was logged. Please try again shortly.",
        "de": "Der Fehler wurde protokolliert. Bitte später erneut versuchen.",
    },
    "err.home": {"fa": "بازگشت به خانه", "en": "Back home", "de": "Zur Startseite"},
    "footer.rights": {"fa": "همهٔ حقوق محفوظ است.", "en": "All rights reserved.", "de": "Alle Rechte vorbehalten."},
    "footer.built": {"fa": "ساخته‌شده با جنگو", "en": "Built with Django", "de": "Gebaut mit Django"},

    # ── command palette ───────────────────────────────────────────────────
    "cmd.open": {"fa": "جست‌وجو", "en": "Search", "de": "Suche"},
    "cmd.placeholder": {"fa": "جست‌وجوی صفحه یا موضوع…", "en": "Page or topic…", "de": "Seite oder Thema…"},
    "cmd.empty": {"fa": "نتیجه‌ای نبود", "en": "No results", "de": "Keine Treffer"},
    "cmd.pages": {"fa": "صفحه‌ها", "en": "Pages", "de": "Seiten"},
    "cmd.actions": {"fa": "میان‌برها", "en": "Shortcuts", "de": "Aktionen"},
    "cmd.move": {"fa": "جابه‌جایی", "en": "move", "de": "wählen"},
    "cmd.go": {"fa": "باز کردن", "en": "open", "de": "öffnen"},

    # ── furniture added with the 2026 redesign ────────────────────────────
    # Labels and tooltips only. Nothing here says anything about the owner; every
    # value these labels sit next to still comes from the database.
    "nav.breadcrumb": {"fa": "مسیر صفحه", "en": "Breadcrumb", "de": "Brotkrümelpfad"},
    "tip.open": {"fa": "باز کردن", "en": "Open", "de": "Öffnen"},
    "tip.new_tab": {"fa": "در زبانهٔ جدید باز می‌شود", "en": "Opens in a new tab", "de": "Öffnet in neuem Tab"},
    "tip.filter": {"fa": "پروژه‌های همین برچسب", "en": "Projects with this tag", "de": "Projekte mit diesem Tag"},
    "home.at_a_glance": {"fa": "در یک نگاه", "en": "At a glance", "de": "Auf einen Blick"},
    "facts.location": {"fa": "موقعیت", "en": "Location", "de": "Standort"},
    "facts.availability": {"fa": "وضعیت همکاری", "en": "Availability", "de": "Verfügbarkeit"},
    "facts.latest_role": {"fa": "آخرین نقش", "en": "Latest role", "de": "Letzte Position"},
    "facts.core_stack": {"fa": "ابزار اصلی", "en": "Core tools", "de": "Kernwerkzeuge"},
    "skills.primary": {"fa": "مهارت اصلی", "en": "Core skill", "de": "Kernkompetenz"},
    "projects.read_case": {"fa": "جزئیات", "en": "Read more", "de": "Mehr lesen"},
    "exp.duration": {"fa": "مدت", "en": "Duration", "de": "Dauer"},
    "dur.year": {"fa": "سال", "en": "yr", "de": "J."},
    "dur.years": {"fa": "سال", "en": "yrs", "de": "J."},
    "dur.month": {"fa": "ماه", "en": "mo", "de": "Mon."},
    "dur.months": {"fa": "ماه", "en": "mos", "de": "Mon."},
    "dur.and": {"fa": " و ", "en": " ", "de": " "},
    "resume.profile": {"fa": "خلاصه", "en": "Profile", "de": "Profil"},
    "resume.skills": {"fa": "مهارت‌ها", "en": "Skills", "de": "Kenntnisse"},
    "channel.email": {"fa": "ایمیل", "en": "Email", "de": "E-Mail"},
    "channel.telegram": {"fa": "تلگرام", "en": "Telegram", "de": "Telegram"},
    "channel.github": {"fa": "گیت‌هاب", "en": "GitHub", "de": "GitHub"},
    "channel.linkedin": {"fa": "لینکدین", "en": "LinkedIn", "de": "LinkedIn"},
    "channel.phone": {"fa": "تلفن", "en": "Phone", "de": "Telefon"},
    "card.vcf": {"fa": "فایل vCard", "en": "vCard file", "de": "vCard-Datei"},
    "footer.explore": {"fa": "گشت‌وگذار", "en": "Explore", "de": "Entdecken"},
    "footer.career": {"fa": "کارنامه", "en": "Career", "de": "Karriere"},
    "footer.connect": {"fa": "ارتباط", "en": "Connect", "de": "Vernetzen"},
    "footer.sitemap": {"fa": "نقشهٔ سایت", "en": "Sitemap", "de": "Sitemap"},
    "footer.top": {"fa": "بازگشت به بالا", "en": "Back to top", "de": "Nach oben"},
}


def t(key: str, lang: str | None = None) -> str:
    """Look one string up. An unknown key returns the key, loudly and visibly."""
    code = (lang or get_language() or DEFAULT_LANG).split("-")[0]
    entry = STRINGS.get(key)
    if entry is None:
        return key
    return entry.get(code) or entry.get(DEFAULT_LANG) or key
