"""
Content models.

Everything a visitor reads comes from here, so the whole site is editable
without a deploy. Nothing else in the project holds copy.

── How translation works ──────────────────────────────────────────────────
A translated field is not one column plus a side table; it is one real column
per language, named `<field>_<lang>`. `@i18n_fields(...)` writes those columns
so the model body stays readable, and `Translatable.tr("title")` reads the
active language with a fallback chain.

Why this rather than django-modeltranslation or a per-language row: it is one
dependency fewer, every query stays a plain query with no joins, the stock
admin renders the three inputs side by side for free, and adding a fourth
language is one entry in settings.LANGUAGES plus one migration. The cost is
that a language you never fill in falls back — which is the behaviour a
personal site wants anyway.
"""

from __future__ import annotations

from urllib.parse import urlsplit

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import get_language

LANG_CODES: tuple[str, ...] = tuple(code for code, _ in settings.LANGUAGES)
DEFAULT_LANG: str = settings.LANGUAGE_CODE
# Order a missing translation falls back through. Persian first because it is
# the language every field is guaranteed to be filled in.
FALLBACK_CHAIN: tuple[str, ...] = (DEFAULT_LANG,) + tuple(
    c for c in LANG_CODES if c != DEFAULT_LANG
)


def i18n_fields(**fields):
    """Class decorator adding `<name>_<lang>` columns for every language.

    Usage:  @i18n_fields(title=lambda: models.CharField(max_length=200))

    The factory is called once per language because a Django field instance
    cannot be attached to two models (or two names) at once.

    Every language except Persian is optional. Persian is required too unless
    the factory itself says `blank=True`, which is how a field that is optional
    in every language (a post written only in English) stays optional.
    """

    def decorate(cls):
        for name, factory in fields.items():
            for code in LANG_CODES:
                field = factory()
                field.blank = field.blank or code != DEFAULT_LANG
                field.verbose_name = f"{name} [{code}]"
                cls.add_to_class(f"{name}_{code}", field)
        cls.I18N_FIELDS = tuple(fields)
        return cls

    return decorate


class Translatable(models.Model):
    """Mixin giving every translated model the same read path."""

    I18N_FIELDS: tuple[str, ...] = ()

    class Meta:
        abstract = True

    def tr(self, name: str) -> str:
        active = (get_language() or DEFAULT_LANG).split("-")[0]
        for code in (active, *FALLBACK_CHAIN):
            value = getattr(self, f"{name}_{code}", "")
            if value:
                return value
        return ""

    def languages_with(self, name: str) -> list[str]:
        """The languages `name` is really written in, fallback order first."""
        return [code for code in FALLBACK_CHAIN if getattr(self, f"{name}_{code}", "")]


class TimeStamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ── Profile: one row, the person ───────────────────────────────────────────
@i18n_fields(
    full_name=lambda: models.CharField(max_length=120),
    headline=lambda: models.CharField(max_length=160, help_text="One line under the name."),
    intro=lambda: models.TextField(help_text="Two or three sentences on the home hero."),
    bio=lambda: models.TextField(blank=True, help_text="Long form, Markdown. Shown on /about/."),
    location=lambda: models.CharField(max_length=80, blank=True),
    now=lambda: models.CharField(max_length=200, blank=True, help_text="What you are working on right now."),
    languages=lambda: models.CharField(
        max_length=160,
        blank=True,
        default="",
        help_text="Spoken languages and levels, e.g. 'Persian native · English C1 · German A1'. "
        "A German CV is expected to state these; the résumé page shows it in the fact bar.",
    ),
    availability=lambda: models.CharField(max_length=80, blank=True, help_text="e.g. open to work"),
    # ── search engines ──
    seo_title=lambda: models.CharField(
        max_length=70,
        blank=True,
        default="",
        help_text="The home page <title>, up to ~60 characters: name plus what you do. "
        "Falls back to the name.",
    ),
    seo_description=lambda: models.CharField(
        max_length=170,
        blank=True,
        default="",
        help_text="The home page meta description — the two lines under the link in "
        "search results. 120–160 characters. Falls back to the intro.",
    ),
    # ── project work, the /services/ page and the home band ──
    offer_title=lambda: models.CharField(
        max_length=120,
        blank=True,
        default="",
        help_text="Headline of the services offer. Empty hides the page, the nav link and the home band.",
    ),
    offer_lede=lambda: models.TextField(blank=True, default="", help_text="One or two sentences under it."),
    offer_body=lambda: models.TextField(
        blank=True,
        default="",
        help_text="Markdown. The long form on /services/ — what you build, how a project runs.",
    ),
)
class Profile(Translatable, TimeStamped):
    """Singleton. `Profile.load()` is the only way anything reads it."""

    avatar = models.ImageField(upload_to="profile/", blank=True)
    og_image = models.ImageField(
        upload_to="profile/",
        blank=True,
        help_text="The picture a shared link shows on LinkedIn, Telegram, WhatsApp or X. "
        "1200×630 px. Falls back to the avatar.",
    )
    resume_file = models.FileField(upload_to="profile/", blank=True)
    # Faint photographs behind a page's head. They are drawn in the page's own
    # accent (the colour is dropped, only the light and shade are kept), so any
    # photo reads as part of the palette in both themes. Empty draws nothing.
    backdrop_services = models.ImageField(
        upload_to="profile/",
        blank=True,
        help_text="Faint photo behind the head of /services/. Portrait, ~800 px wide.",
    )
    backdrop_resume = models.ImageField(
        upload_to="profile/",
        blank=True,
        help_text="Faint photo inside the résumé's header card. Portrait, ~800 px wide.",
    )

    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=32, blank=True)
    telegram = models.CharField(max_length=64, blank=True, help_text="username, no @")
    github = models.CharField(max_length=64, blank=True)
    linkedin = models.CharField(max_length=120, blank=True)
    twitter = models.CharField(max_length=64, blank=True)
    website = models.URLField(blank=True)

    is_available = models.BooleanField(default=True)

    class Meta:
        verbose_name = "profile"

    def __str__(self) -> str:
        return self.full_name_fa or "profile"

    @property
    def share_image(self):
        return self.og_image or self.avatar

    def save(self, *args, **kwargs):
        self.pk = 1  # there is exactly one person on a personal site
        super().save(*args, **kwargs)

    @classmethod
    def load(cls) -> "Profile":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def links(self) -> list[dict]:
        """The contact channels, in the order they should be offered."""
        out = []
        if self.email:
            out.append({"key": "email", "label": self.email, "href": f"mailto:{self.email}", "copy": self.email})
        if self.telegram:
            handle = self.telegram.lstrip("@")
            out.append({"key": "telegram", "label": f"@{handle}", "href": f"https://t.me/{handle}", "copy": f"@{handle}"})
        if self.github:
            handle = self.github.strip("/").split("/")[-1]
            out.append({"key": "github", "label": handle, "href": f"https://github.com/{handle}", "copy": f"https://github.com/{handle}"})
        if self.linkedin:
            handle = self.linkedin.strip("/").split("/")[-1]
            out.append({"key": "linkedin", "label": handle, "href": f"https://www.linkedin.com/in/{handle}", "copy": f"https://www.linkedin.com/in/{handle}"})
        if self.phone:
            out.append({"key": "phone", "label": self.phone, "href": f"tel:{self.phone}", "copy": self.phone})
        return out


# ── What a client gets: the cards on /services/ and the home band ──────────
@i18n_fields(
    title=lambda: models.CharField(max_length=80),
    body=lambda: models.CharField(max_length=280),
)
class Service(Translatable):
    """One promise to a client — end to end, fast delivery, agreed price.

    A row rather than a sentence in `offer_body` because each one is a card,
    and a card needs its own title, icon and place in the order.
    """

    class Icon(models.TextChoices):
        LAYERS = "layers", "layers"
        CLOCK = "clock", "clock"
        TARGET = "target", "target"
        BRIEFCASE = "briefcase", "briefcase"
        CODE = "code", "code"
        DATABASE = "database", "database"
        SPARKLE = "sparkle", "sparkle"
        CHECK = "check", "check"

    icon = models.CharField(max_length=16, choices=Icon.choices, default=Icon.SPARKLE)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("order", "pk")

    def __str__(self) -> str:
        return self.title_fa or f"service {self.pk}"


# ── Skills ─────────────────────────────────────────────────────────────────
@i18n_fields(name=lambda: models.CharField(max_length=80))
class SkillGroup(Translatable):
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("order", "pk")

    def __str__(self) -> str:
        return self.name_fa or f"group {self.pk}"


class Skill(models.Model):
    """Deliberately has no percentage. A number nobody can verify buys nothing."""

    group = models.ForeignKey(SkillGroup, on_delete=models.CASCADE, related_name="skills")
    name = models.CharField(max_length=60, help_text="Technology names stay Latin in every language.")
    order = models.PositiveIntegerField(default=0)
    is_primary = models.BooleanField(default=False, help_text="Shown in the home hero strip.")

    class Meta:
        ordering = ("order", "pk")

    def __str__(self) -> str:
        return self.name


# ── Tags: shared by projects and posts ─────────────────────────────────────
@i18n_fields(name=lambda: models.CharField(max_length=60))
class Tag(Translatable):
    slug = models.SlugField(max_length=60, unique=True)

    class Meta:
        ordering = ("slug",)

    def __str__(self) -> str:
        return self.slug


# ── Projects ───────────────────────────────────────────────────────────────
@i18n_fields(
    title=lambda: models.CharField(max_length=140),
    summary=lambda: models.CharField(max_length=240, help_text="One sentence, shown on the card."),
    role=lambda: models.CharField(max_length=120, blank=True),
    problem=lambda: models.TextField(blank=True, help_text="Markdown. What needed solving."),
    body=lambda: models.TextField(blank=True, help_text="Markdown. What you built and why."),
    outcome=lambda: models.CharField(max_length=240, blank=True, help_text="The result, in one line."),
)
class Project(Translatable, TimeStamped):
    slug = models.SlugField(max_length=140, unique=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    stack = models.CharField(max_length=200, blank=True, help_text="Comma separated, Latin, e.g. Django, Postgres")
    cover = models.ImageField(upload_to="projects/", blank=True)
    repo_url = models.URLField(blank=True)
    demo_url = models.URLField(blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name="projects")

    is_featured = models.BooleanField(default=False, help_text="Appears on the home page.")
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("order", "-year", "-pk")

    def __str__(self) -> str:
        return self.slug

    def get_absolute_url(self) -> str:
        return reverse("project_detail", args=[self.slug])

    @property
    def stack_list(self) -> list[str]:
        return [part.strip() for part in self.stack.split(",") if part.strip()]


# ── Career and education ───────────────────────────────────────────────────
@i18n_fields(
    org=lambda: models.CharField(max_length=140),
    role=lambda: models.CharField(max_length=140),
    description=lambda: models.TextField(blank=True, help_text="Markdown. What you actually did."),
    location=lambda: models.CharField(max_length=80, blank=True),
)
class Experience(Translatable):
    class Kind(models.TextChoices):
        WORK = "work", "Work"
        EDUCATION = "education", "Education"

    kind = models.CharField(max_length=16, choices=Kind.choices, default=Kind.WORK)
    start = models.DateField()
    end = models.DateField(null=True, blank=True, help_text="Leave empty if this is current.")
    url = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("order", "-start")

    def __str__(self) -> str:
        return f"{self.role_fa} @ {self.org_fa}"

    @property
    def is_current(self) -> bool:
        return self.end is None


# ── Writing ────────────────────────────────────────────────────────────────
class Written(Translatable, TimeStamped):
    """What a post and an article share: they are written in whichever
    languages they are written in, and every page about them has to know which.

    A concrete subclass has `title_*`, `body_*`, `cover`, `published_at` and a
    related `images` set.
    """

    class Meta:
        abstract = True

    @property
    def languages(self) -> list[str]:
        """Languages this piece is actually written in: a title of its own."""
        return self.languages_with("title")

    @property
    def content_language(self) -> str:
        """The language the reader is shown: theirs if written, else the first there is."""
        active = (get_language() or DEFAULT_LANG).split("-")[0]
        langs = self.languages
        if active in langs or not langs:
            return active
        return langs[0]

    @property
    def lead_image(self):
        """The picture for a shared link: the cover, else the first body image."""
        if self.cover:
            return self.cover
        first = next(iter(self.images.all()), None)
        return first.image if first else None

    @property
    def reading_minutes(self) -> int:
        """Counted on the body the reader is actually being shown."""
        words = len(self.tr("body").split())
        return max(1, round(words / 200))


# A post is written in whichever languages it is written in — a LinkedIn post
# is often English only — so no language is required here and `clean()` asks
# for one complete language instead. A language with no title of its own is
# served with the fallback but marked noindex, so a search engine never
# indexes a Persian article under /en/.
POST_BODY_HELP = (
    "Markdown. A line break stays a line break, so text pasted from LinkedIn keeps "
    "its shape. ## heading · **bold** · [text](https://…) for a link · a bare "
    "https://… link works too · ![description](/media/…) for an image — upload "
    "images at the bottom of this page and copy their line from there."
)


@i18n_fields(
    title=lambda: models.CharField(max_length=180, blank=True),
    excerpt=lambda: models.CharField(
        max_length=280,
        blank=True,
        help_text="One or two sentences. Shown in the list and used as the search "
        "result description, so 120–160 characters reads best.",
    ),
    body=lambda: models.TextField(blank=True, help_text=POST_BODY_HELP),
)
class Post(Written):
    slug = models.SlugField(
        max_length=180,
        unique=True,
        help_text="The address: /blog/<slug>/. Latin, lowercase, hyphens — e.g. "
        "sql-server-locking. Keep it stable once published.",
    )
    cover = models.ImageField(
        upload_to="posts/",
        blank=True,
        help_text="Shown above the post and as the picture when the link is shared. 1200×630 px reads best.",
    )
    original_url = models.URLField(
        blank=True,
        max_length=500,
        help_text="Where this was first published — a LinkedIn post, X, Virgool, Medium. "
        "Shown under the post as a link to the original.",
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="posts")
    published_at = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=True)

    # host → (platform key, icon id). The key is `platform.<key>` in i18n.py.
    PLATFORMS = {
        "linkedin.com": ("linkedin", "linkedin"),
        "lnkd.in": ("linkedin", "linkedin"),
        "x.com": ("x", "external"),
        "twitter.com": ("x", "external"),
        "github.com": ("github", "github"),
        "t.me": ("telegram", "telegram"),
        "medium.com": ("medium", "external"),
        "virgool.io": ("virgool", "external"),
        "dev.to": ("devto", "external"),
    }

    class Meta:
        ordering = ("-published_at", "-pk")

    def __str__(self) -> str:
        return self.slug

    def clean(self):
        if not self.languages:
            raise ValidationError("Write the title and body in at least one language.")
        for code in LANG_CODES:
            if getattr(self, f"title_{code}") and not getattr(self, f"body_{code}"):
                raise ValidationError({f"body_{code}": "A title in this language needs a body too."})

    def get_absolute_url(self) -> str:
        return reverse("post_detail", args=[self.slug])

    @property
    def original(self) -> dict | None:
        """{"key", "icon", "url"} for the original-post link, or None."""
        if not self.original_url:
            return None
        host = (urlsplit(self.original_url).hostname or "").lower().removeprefix("www.")
        for domain, (key, icon) in self.PLATFORMS.items():
            if host == domain or host.endswith("." + domain):
                return {"key": key, "icon": icon, "url": self.original_url}
        return {"key": "web", "icon": "external", "url": self.original_url}


class PostImage(models.Model):
    """An image used inside a post body.

    Uploaded from the post's own admin page, which then shows the Markdown line
    to paste — so a picture in the middle of a post needs no second tool.
    """

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="posts/body/")
    alt = models.CharField(
        max_length=200,
        blank=True,
        help_text="What the image shows, in a few words. Read aloud by screen readers and by Google Images.",
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("order", "pk")

    def __str__(self) -> str:
        return self.alt or self.image.name

    @property
    def markdown(self) -> str:
        return f"![{self.alt}]({self.image.url})" if self.image else ""


# ── Articles ───────────────────────────────────────────────────────────────
# An article is the long, citable piece — a paper in a journal or a
# conference, a technical write-up on delay analysis or scheduling — where a
# post is a note. It can live entirely on the site (a Markdown body), or be a
# published paper shown by its abstract with the PDF and the publisher's link
# beside it. Like a post, it is written in whichever languages it exists in.
@i18n_fields(
    title=lambda: models.CharField(max_length=220, blank=True),
    abstract=lambda: models.TextField(
        blank=True,
        help_text="The abstract, or two or three sentences on what the article argues. "
        "Shown in the list and at the top of the page; the first ~160 characters are "
        "the search result description.",
    ),
    body=lambda: models.TextField(
        blank=True,
        help_text="Optional for a paper that is published elsewhere — the abstract and the "
        "PDF are then the page. " + POST_BODY_HELP,
    ),
    venue=lambda: models.CharField(
        max_length=220,
        blank=True,
        help_text="Where it was published: journal, conference or magazine, e.g. "
        "'12th International Conference on Civil Engineering'. Empty for an article "
        "written for this site.",
    ),
)
class Article(Written):
    slug = models.SlugField(
        max_length=180,
        unique=True,
        help_text="The address: /articles/<slug>/. Latin, lowercase, hyphens — e.g. "
        "delay-analysis-methods. Keep it stable once published.",
    )
    authors = models.CharField(
        max_length=300,
        blank=True,
        help_text="Everyone who wrote it, in the order the paper lists them, e.g. "
        "'H. Naderirad, A. Author'. Empty for an article written alone.",
    )
    cover = models.ImageField(
        upload_to="articles/",
        blank=True,
        help_text="Shown above the article and as the picture when the link is shared. 1200×630 px reads best.",
    )
    pdf = models.FileField(
        upload_to="articles/pdf/",
        blank=True,
        help_text="The full text as a PDF. Offered as a download on the article page.",
    )
    doi = models.CharField(
        max_length=120,
        blank=True,
        help_text="e.g. 10.1016/j.autcon.2024.105000 — without https://doi.org/.",
    )
    external_url = models.URLField(
        blank=True,
        max_length=500,
        help_text="The article on the publisher's site, Civilica, ResearchGate or LinkedIn.",
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="articles")
    published_at = models.DateTimeField(
        default=timezone.now,
        help_text="The publication date. The list is ordered by it.",
    )
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ("-published_at", "-pk")

    def __str__(self) -> str:
        return self.slug

    def clean(self):
        if not self.languages:
            raise ValidationError("Write the title in at least one language.")
        for code in LANG_CODES:
            if getattr(self, f"title_{code}") and not (
                getattr(self, f"abstract_{code}") or getattr(self, f"body_{code}")
            ):
                raise ValidationError(
                    {f"abstract_{code}": "A title in this language needs an abstract or a body too."}
                )
        self.doi = self.doi.strip().removeprefix("https://doi.org/").removeprefix("doi:").strip()

    def get_absolute_url(self) -> str:
        return reverse("article_detail", args=[self.slug])

    @property
    def doi_url(self) -> str:
        return f"https://doi.org/{self.doi}" if self.doi else ""

    @property
    def reading_minutes(self) -> int:
        """A paper with no body on the site is read as its abstract."""
        words = len((self.tr("body") or self.tr("abstract")).split())
        return max(1, round(words / 200))


class ArticleImage(models.Model):
    """An image used inside an article body, uploaded on the article's admin page."""

    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="articles/body/")
    alt = models.CharField(
        max_length=200,
        blank=True,
        help_text="What the image shows, in a few words. Read aloud by screen readers and by Google Images.",
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("order", "pk")

    def __str__(self) -> str:
        return self.alt or self.image.name

    @property
    def markdown(self) -> str:
        return f"![{self.alt}]({self.image.url})" if self.image else ""


# ── Messages from the contact form ─────────────────────────────────────────
class Message(models.Model):
    """A message from the contact form.

    Its status is changed from the admin or from the buttons under its
    notification in the Bale bot (apps/core/bale.py) — the same field either way.
    """

    class Status(models.TextChoices):
        NEW = "new", "جدید"
        READ = "read", "خوانده شده"
        REJECTED = "rejected", "رد شده"
        ARCHIVED = "archived", "بایگانی"
        STARRED = "starred", "محبوب"

    name = models.CharField(max_length=120)
    # A way to answer is required, not a particular one: many readers in Iran
    # would rather be called or messaged than emailed. At least one of the two
    # is enforced by the form and, as the last line, by the constraint below.
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)  # normalised: digits, optional leading +
    subject = models.CharField(max_length=160, blank=True)
    body = models.TextField()
    language = models.CharField(max_length=8, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.NEW, db_index=True)
    status_changed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(email="") | ~models.Q(phone=""),
                name="message_has_reply_channel",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} — {self.created_at:%Y-%m-%d}"
