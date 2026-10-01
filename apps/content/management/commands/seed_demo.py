"""
Seed the site with placeholder content in all three languages.

Idempotent: it upserts by slug, so running it twice changes nothing. It exists
so a fresh clone renders a complete site instead of an empty shell — every
string it writes is a placeholder to replace in the admin.

    python manage.py seed_demo
    python manage.py seed_demo --wipe   # start over
"""

from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.content.models import (
    Experience,
    Post,
    Profile,
    Project,
    Skill,
    SkillGroup,
    Tag,
)


class Command(BaseCommand):
    help = "Fill the database with three-language placeholder content."

    def add_arguments(self, parser):
        parser.add_argument("--wipe", action="store_true", help="Delete existing content first.")

    @transaction.atomic
    def handle(self, *args, **options):
        if options["wipe"]:
            for model in (Project, Post, Experience, Skill, SkillGroup, Tag):
                model.objects.all().delete()
            self.stdout.write(self.style.WARNING("wiped existing content"))

        self._profile()
        tags = self._tags()
        self._skills()
        self._projects(tags)
        self._experience()
        self._posts(tags)
        self.stdout.write(self.style.SUCCESS("seeded — every string here is a placeholder"))

    # ── profile ───────────────────────────────────────────────────────────
    def _profile(self):
        p = Profile.load()
        p.full_name_fa = "حسن نادری‌راد"
        p.full_name_en = "Hassan Naderirad"
        p.full_name_de = "Hassan Naderirad"

        p.headline_fa = "برنامه‌ریزی و کنترل پروژه‌های عمرانی"
        p.headline_en = "Planning and control of civil engineering projects"
        p.headline_de = "Planung und Steuerung von Bauprojekten"

        p.intro_fa = "متن نمونه‌ی معرفی — دو یا سه جمله درباره‌ی کاری که انجام می‌دهید."
        p.intro_en = "Placeholder introduction — two or three sentences about what you do."
        p.intro_de = "Platzhalter — zwei oder drei Sätze darüber, was Sie tun."

        p.bio_fa = "### چطور کار می‌کنم

*این متن نمونه است و باید با روایت خودتان جایگزین شود.*"
        p.bio_en = "### How I work

*Placeholder text — replace with your own.*"
        p.bio_de = "### Wie ich arbeite

*Platzhaltertext — bitte ersetzen.*"

        p.location_fa, p.location_en, p.location_de = "تهران، ایران", "Tehran, Iran", "Teheran, Iran"
        p.now_fa = "متن نمونه — کاری که این روزها روی آن هستید."
        p.now_en = "Placeholder — what you are working on right now."
        p.now_de = "Platzhalter — woran Sie gerade arbeiten."
        p.availability_fa, p.availability_en, p.availability_de = "آمادهٔ همکاری", "Open to work", "Offen für Projekte"

        p.email = "hello@example.com"
        p.github = ""
        p.linkedin = ""
        p.telegram = ""
        p.is_available = True
        p.save()

    # ── tags ──────────────────────────────────────────────────────────────
    def _tags(self) -> dict[str, Tag]:
        rows = [
            ("planning", "برنامه‌ریزی", "Planning", "Terminplanung"),
            ("control", "کنترل پروژه", "Project control", "Projektsteuerung"),
            ("delay", "تأخیرات", "Delays", "Verzug"),
            ("notes", "یادداشت", "Notes", "Notizen"),
        ]
        out = {}
        for slug, fa, en, de in rows:
            tag, _ = Tag.objects.update_or_create(
                slug=slug, defaults={"name_fa": fa, "name_en": en, "name_de": de}
            )
            out[slug] = tag
        return out

    # ── skills ────────────────────────────────────────────────────────────
    def _skills(self):
        groups = [
            (("نرم‌افزارها", "Software", "Software"), 0,
             [("Primavera P6", True), ("MS Project", True), ("Excel", False)]),
            (("روش‌ها", "Methods", "Methoden"), 1,
             [("CPM", True), ("WBS", False), ("Delay analysis", True)]),
        ]
        for (fa, en, de), order, skills in groups:
            group, _ = SkillGroup.objects.update_or_create(
                name_fa=fa, defaults={"name_en": en, "name_de": de, "order": order}
            )
            group.skills.all().delete()
            for i, (name, primary) in enumerate(skills):
                Skill.objects.create(group=group, name=name, order=i, is_primary=primary)

    # ── projects ──────────────────────────────────────────────────────────
    def _projects(self, tags):
        rows = [
            ("sample-project-a", 2026, "Primavera P6, CPM", ["planning", "control"],
             ("پروژه‌ی نمونه‌ی الف", "Sample project A", "Beispielprojekt A")),
            ("sample-project-b", 2025, "MS Project, Delay analysis", ["delay", "control"],
             ("پروژه‌ی نمونه‌ی ب", "Sample project B", "Beispielprojekt B")),
        ]
        for order, (slug, year, stack, tag_slugs, (fa, en, de)) in enumerate(rows):
            defaults = {
                "year": year, "stack": stack, "is_featured": True, "is_published": True, "order": order,
                "title_fa": fa, "title_en": en, "title_de": de,
                "summary_fa": "شرح یک‌خطی نمونه.", "summary_en": "A placeholder one-line summary.",
                "summary_de": "Platzhalter.",
                "body_fa": "*این متن نمونه است.*", "body_en": "*Placeholder text.*", "body_de": "*Platzhaltertext.*",
            }
            project, _ = Project.objects.update_or_create(slug=slug, defaults=defaults)
            project.tags.set([tags[s] for s in tag_slugs])

    # ── experience ────────────────────────────────────────────────────────
    def _experience(self):
        rows = [
            (Experience.Kind.WORK, date(2024, 1, 1), None,
             ("نام شرکت", "کارشناس برنامه‌ریزی و کنترل پروژه"), ("Company name", "Planning and control engineer"),
             ("Firmenname", "Projektsteuerer")),
            (Experience.Kind.EDUCATION, date(2020, 9, 1), date(2023, 7, 1),
             ("نام دانشگاه", "کارشناسی ارشد مهندسی عمران"), ("University name", "MSc, Civil Engineering"),
             ("Universität", "M.Sc. Bauingenieurwesen")),
        ]
        for order, (kind, start, end, fa, en, de) in enumerate(rows):
            defaults = {"kind": kind, "start": start, "end": end, "order": order}
            for code, (org, role) in (("fa", fa), ("en", en), ("de", de)):
                defaults[f"org_{code}"] = org
                defaults[f"role_{code}"] = role
            Experience.objects.update_or_create(org_fa=fa[0], start=start, defaults=defaults)

    # ── posts ─────────────────────────────────────────────────────────────
    def _posts(self, tags):
        defaults = {
            "published_at": timezone.now() - timezone.timedelta(days=3),
            "is_published": True,
            "title_fa": "نوشته‌ی نمونه", "title_en": "A sample post", "title_de": "Ein Beispielbeitrag",
            "excerpt_fa": "خلاصه‌ی نمونه.", "excerpt_en": "A placeholder excerpt.", "excerpt_de": "Platzhalter.",
            "body_fa": "*این نوشته‌ی نمونه است.*", "body_en": "*Placeholder post.*", "body_de": "*Platzhalterbeitrag.*",
        }
        post, _ = Post.objects.update_or_create(slug="sample-post", defaults=defaults)
        post.tags.set([tags["notes"]])
