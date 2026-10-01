"""
Stock Django admin — the interim way to edit content.

The custom lightweight panel is a later piece of work (see CLAUDE.md). Until it
exists this is what makes the database writable, and it costs nothing: the
per-language columns render as three plain inputs side by side.

The post and article forms are the screens written for regular use, so they
get the most care: one block per language, a body box big enough to write in,
and images uploaded on the same page with the Markdown line to paste already
built.
"""

from django.contrib import admin
from django.contrib.admin.widgets import AdminFileWidget
from django.db import models
from django.shortcuts import redirect
from django.utils.html import format_html

from .models import (
    LANG_CODES,
    Article,
    ArticleImage,
    Experience,
    Message,
    Post,
    PostImage,
    Profile,
    Project,
    Service,
    Skill,
    SkillGroup,
    Tag,
)

LANG_NAMES = {"fa": "فارسی — Persian", "en": "English", "de": "Deutsch — German"}


def _per_language(*names):
    return [
        (LANG_NAMES.get(code, code), {"fields": [f"{name}_{code}" for name in names]})
        for code in LANG_CODES
    ]


IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif", ".svg")


class UploadWidget(AdminFileWidget):
    """The stock file input, plus what it never tells you.

    A chosen file only reaches the server when the form is saved, and the stock
    input shows nothing but its name. This one shows the file that is live now,
    a preview of the one waiting, an undo for the choice, and — through
    upload.js — a bar that stays on screen until «ذخیره» is pressed.
    """

    class Media:
        css = {"all": ["content/upload.css"]}
        js = ["content/upload.js"]

    def render(self, name, value, attrs=None, renderer=None):
        live = ""
        if value and getattr(value, "url", None):
            if value.name.lower().endswith(IMAGE_EXTENSIONS):
                live = format_html(
                    '<a class="upload-live" href="{0}" target="_blank" rel="noopener" '
                    'title="روی سایت همین است"><img src="{0}" alt=""></a>',
                    value.url,
                )
        return format_html(
            '<div class="upload" data-upload>{}<div class="upload-field">{}'
            '<div class="upload-new" hidden><img alt="" hidden>'
            '<span><b class="upload-name"></b><small>با «ذخیره» روی سایت می‌نشیند</small></span>'
            '<button type="button" class="button" data-upload-undo>✕ منصرف شدم</button></div>'
            '<small class="upload-gone" hidden>با «ذخیره» از سایت برداشته می‌شود</small>'
            "</div></div>",
            live,
            super().render(name, value, attrs, renderer),
        )


# Every admin that has a file field uses it. ImageField needs its own key: the
# admin matches the field's own class before its parent's.
UPLOADS = {
    models.ImageField: {"widget": UploadWidget(attrs={"accept": "image/*"})},
    models.FileField: {"widget": UploadWidget},
}


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """One row, so the list is skipped and the photos come first.

    The form is long (every text in three languages); before this the file
    inputs sat half-way down and «ذخیره» at the very bottom, so a chosen photo
    looked like it had been taken while nothing had been sent.
    """

    formfield_overrides = UPLOADS
    save_on_top = True
    fieldsets = [
        (
            "عکس‌ها و فایل‌ها",
            {
                "fields": ("avatar", "og_image", "backdrop_services", "backdrop_resume", "resume_file"),
                "description": "فایل را انتخاب کنید و «ذخیره» را بزنید؛ تا ذخیره نشود روی سایت نمی‌آید. "
                "برای برداشتن عکسی که الان روی سایت است، تیک «پاک کردن» کنارش را بزنید و ذخیره کنید.",
            },
        ),
        ("تماس", {"fields": ("email", "phone", "telegram", "linkedin", "github", "twitter", "website", "is_available")}),
        *_per_language(*Profile.I18N_FIELDS),
    ]
    # The model's help texts for these two are missing; said here to spare a migration.
    HELP = {
        "avatar": "Your portrait: home page, about, résumé and the business card. Square, at least 700×700 px.",
        "resume_file": "The file behind every «download résumé» button. PDF.",
    }

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)
        if field and db_field.name in self.HELP:
            field.help_text = self.HELP[db_field.name]
        return field

    def changelist_view(self, request, extra_context=None):
        # A list of one row is a detour, and «ذخیره» lands here: send it back
        # to the form, where the success message and the new photos show.
        return redirect("admin:content_profile_change", Profile.load().pk)

    def has_add_permission(self, request):
        return not Profile.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title_fa", "title_en", "icon", "order")
    list_editable = ("icon", "order")


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 1


@admin.register(SkillGroup)
class SkillGroupAdmin(admin.ModelAdmin):
    list_display = ("name_fa", "name_en", "order")
    inlines = [SkillInline]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("slug", "name_fa", "name_en", "name_de")
    prepopulated_fields = {"slug": ("name_en",)}


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    formfield_overrides = UPLOADS
    list_display = ("slug", "title_fa", "year", "is_featured", "is_published", "order")
    list_filter = ("is_featured", "is_published", "tags")
    list_editable = ("is_featured", "is_published", "order")
    search_fields = ("slug", "title_fa", "title_en", "title_de")
    filter_horizontal = ("tags",)


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("org_fa", "role_fa", "kind", "start", "end")
    list_filter = ("kind",)


class _ImageInline(admin.TabularInline):
    extra = 1
    formfield_overrides = UPLOADS
    fields = ("image", "alt", "order", "snippet")
    readonly_fields = ("snippet",)

    @admin.display(description="Markdown to paste into the body")
    def snippet(self, obj):
        if not obj.pk or not obj.image:
            return "Save (and continue editing) to get the line to paste."
        return format_html(
            '<code style="user-select:all;direction:ltr;unicode-bidi:isolate">{}</code> '
            '<button type="button" class="button" '
            "onclick=\"navigator.clipboard.writeText(this.previousElementSibling.textContent)"
            ".then(()=>{{this.textContent='✓ copied'}})\">copy</button>",
            obj.markdown,
        )


class PostImageInline(_ImageInline):
    model = PostImage


class ArticleImageInline(_ImageInline):
    model = ArticleImage


class _WrittenAdmin(admin.ModelAdmin):
    """What the post and article screens share."""

    formfield_overrides = UPLOADS
    list_filter = ("is_published", "tags")
    list_editable = ("is_published",)
    search_fields = ("slug", *[f"title_{code}" for code in LANG_CODES])
    date_hierarchy = "published_at"
    filter_horizontal = ("tags",)
    prepopulated_fields = {"slug": ("title_en",)}
    save_on_top = True
    TEXT_FIELDS: tuple[str, ...] = ("title_", "body_")

    @admin.display(description="title")
    def title(self, obj):
        return obj.tr("title")

    @admin.display(description="written in")
    def written_in(self, obj):
        return " · ".join(code.upper() for code in obj.languages)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)
        # dir="auto" lets a Persian paragraph sit right-to-left in the same box
        # an English one sits left-to-right in.
        if db_field.name.startswith(self.TEXT_FIELDS):
            field.widget.attrs["dir"] = "auto"
        if db_field.name.startswith("body_"):
            field.widget.attrs.update(rows=20, style="width:100%;max-width:60rem;line-height:1.7")
        return field


@admin.register(Post)
class PostAdmin(_WrittenAdmin):
    list_display = ("slug", "title", "written_in", "published_at", "is_published")
    inlines = [PostImageInline]
    TEXT_FIELDS = ("title_", "excerpt_", "body_")
    fieldsets = [
        (None, {"fields": ("slug", ("published_at", "is_published"), "cover", "original_url", "tags")}),
        *_per_language("title", "excerpt", "body"),
    ]


@admin.register(Article)
class ArticleAdmin(_WrittenAdmin):
    list_display = ("slug", "title", "written_in", "has_pdf", "published_at", "is_published")
    inlines = [ArticleImageInline]
    TEXT_FIELDS = ("title_", "abstract_", "body_", "venue_")
    fieldsets = [
        (None, {"fields": ("slug", ("published_at", "is_published"), "cover", "tags")}),
        (
            "Publication",
            {
                "fields": ("authors", "pdf", "doi", "external_url"),
                "description": "All optional. Fill these in for a paper published in a "
                "journal or a conference; leave them empty for an article written for this site.",
            },
        ),
        *_per_language("title", "venue", "abstract", "body"),
    ]

    @admin.display(description="PDF", boolean=True)
    def has_pdf(self, obj):
        return bool(obj.pdf)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name.startswith("abstract_"):
            field.widget.attrs.update(rows=5, style="width:100%;max-width:60rem;line-height:1.7")
        return field


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "subject", "created_at", "status")
    list_editable = ("status",)
    list_filter = ("status", "language")
    readonly_fields = ("name", "email", "phone", "subject", "body", "language", "created_at", "status_changed_at")
    search_fields = ("name", "email", "phone", "body")
    actions = ("send_to_bale",)

    @admin.action(description="ارسال دوباره به بله")
    def send_to_bale(self, request, queryset):
        from apps.core import bale

        if not bale.enabled():
            self.message_user(request, "BALE_BOT_TOKEN و BALE_CHAT_IDS تنظیم نشده‌اند.", level="warning")
            return
        sent = sum(bale.notify(m, background=False) for m in queryset)
        self.message_user(request, f"{sent} پیام به بله فرستاده شد.")
