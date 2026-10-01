"""
Seed the site with Hassan Naderirad's real content in all three languages.

This is the counterpart to `seed_demo`: same shape, but every string here is
true and traceable to the profile he supplied. It is the reproducible record
of what the live site says, so a claim can be changed in one reviewed place
rather than in an admin form nobody can diff.

    python manage.py seed_profile           # upsert, keeps the database
    python manage.py seed_profile --wipe    # replace projects/skills/roles

── Rules this file follows ────────────────────────────────────────────────
Every claim comes from his own summary: an MSc in civil engineering
(construction management) from Iran University of Science and Technology,
full command of Microsoft Project and Primavera P6, the ICB Level D
certificate, delay analysis and delay layering, and preparing, controlling and
updating schedules. Nothing is added to it — no project names, no employers,
no figures, no years of experience.

The four entries under /projects/ are therefore areas of practice, not client
case studies: each one describes how the work is done, never a result on a
named project. When a real project can be named, it belongs here as its own
`_upsert_project` call, with its year.

Career and education are deliberately absent as timeline rows: an entry needs
real dates, and an empty section renders nothing at all, which reads better
than an invented one. The degree still appears in the headline, the intro and
the biography. Location, spoken languages and contact channels are left empty
for the same reason — they are filled here once he supplies them.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.content.models import (
    Experience,
    Profile,
    Project,
    Service,
    Skill,
    SkillGroup,
    Tag,
)


class Command(BaseCommand):
    help = "Fill the database with Hassan Naderirad's real content, in fa/en/de."

    def add_arguments(self, parser):
        parser.add_argument(
            "--wipe",
            action="store_true",
            help="Delete projects, skills, tags and roles first.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["wipe"]:
            for model in (Project, Experience, Skill, SkillGroup, Tag):
                model.objects.all().delete()
            self.stdout.write(self.style.WARNING("wiped projects, skills, tags and roles"))

        self._profile()
        self._services()
        tags = self._tags()
        self._skills()
        self._projects(tags)
        self.stdout.write(self.style.SUCCESS("seeded — real content, fa/en/de"))

    # ── profile ───────────────────────────────────────────────────────────
    def _profile(self):
        p = Profile.load()

        p.full_name_fa = "حسن نادری‌راد"
        p.full_name_en = "Hassan Naderirad"
        p.full_name_de = "Hassan Naderirad"

        p.headline_fa = "کارشناس ارشد مهندسی عمران، مدیریت ساخت — برنامه‌ریزی و کنترل پروژه"
        p.headline_en = "Civil engineer, MSc in construction management — project planning and control"
        p.headline_de = "Bauingenieur, M.Sc. Baumanagement — Projektplanung und -steuerung"

        p.intro_fa = (
            "برنامه‌ی زمان‌بندی پروژه‌های عمرانی را تهیه، کنترل و به‌روزرسانی می‌کنم؛ پیشرفت را "
            "تحلیل می‌کنم، انحراف‌ها را زود پیدا می‌کنم و برایشان راهکار کنترلی پیشنهاد می‌دهم. "
            "مسلط به Primavera P6 و Microsoft Project، دارای گواهینامه‌ی ICB Level D و مسلط به "
            "آنالیز و لایه‌بندی تأخیرات."
        )
        p.intro_en = (
            "I prepare, control and update the schedules of civil engineering projects — "
            "analysing progress, finding deviations early and proposing the corrective action "
            "for each. Fluent in Primavera P6 and Microsoft Project, ICB Level D certified, and "
            "skilled in delay analysis and delay layering."
        )
        p.intro_de = (
            "Ich erstelle, überwache und aktualisiere Terminpläne für Bauprojekte: Ich werte "
            "den Fortschritt aus, erkenne Abweichungen früh und schlage für jede eine "
            "Steuerungsmaßnahme vor. Sicher in Primavera P6 und Microsoft Project, zertifiziert "
            "nach ICB Level D und versiert in Verzugsanalyse und Verzugsschichtung."
        )

        p.bio_fa = _BIO_FA
        p.bio_en = _BIO_EN
        p.bio_de = _BIO_DE

        p.location_fa = p.location_en = p.location_de = ""
        p.languages_fa = p.languages_en = p.languages_de = ""

        p.now_fa = (
            "در جست‌وجوی همکاری در برنامه‌ریزی و کنترل پروژه، مدیریت ساخت و تحلیل تأخیرات "
            "پروژه‌های عمرانی."
        )
        p.now_en = (
            "Looking for work in project planning and control, construction management and "
            "delay analysis on civil engineering projects."
        )
        p.now_de = (
            "Auf der Suche nach Aufgaben in Projektplanung und -steuerung, Baumanagement und "
            "Verzugsanalyse im Bauwesen."
        )

        p.availability_fa = "آماده‌ی همکاری — برنامه‌ریزی و کنترل پروژه"
        p.availability_en = "Open to work — project planning and control"
        p.availability_de = "Offen für Zusammenarbeit — Projektplanung und -steuerung"

        # ── search results: the home page title and the two lines under it ──
        p.seo_title_fa = "حسن نادری‌راد | برنامه‌ریزی و کنترل پروژه‌های عمرانی"
        p.seo_title_en = "Hassan Naderirad — Project Planning & Control, Civil"
        p.seo_title_de = "Hassan Naderirad — Projektplanung & -steuerung, Bau"
        p.seo_description_fa = (
            "حسن نادری‌راد، کارشناس ارشد مدیریت ساخت از علم و صنعت — برنامه‌ریزی و کنترل پروژه "
            "با Primavera P6 و MSP، تحلیل و لایه‌بندی تأخیرات، دارای ICB Level D."
        )
        p.seo_description_en = (
            "Hassan Naderirad, MSc in construction management (IUST) — project planning and "
            "control in Primavera P6 and MS Project, delay analysis, ICB Level D."
        )
        p.seo_description_de = (
            "Hassan Naderirad, M.Sc. Baumanagement (IUST) — Terminplanung und -steuerung mit "
            "Primavera P6 und MS Project, Verzugsanalyse, ICB Level D."
        )

        # ── project work ──
        p.offer_title_fa = "برنامه‌ریزی و کنترل پروژه‌ی عمرانی شما"
        p.offer_title_en = "Planning and control for your construction project"
        p.offer_title_de = "Planung und Steuerung für Ihr Bauprojekt"
        p.offer_lede_fa = (
            "از برنامه‌ی زمان‌بندی مبنا تا به‌روزرسانی‌های دوره‌ای، گزارش پیشرفت و تحلیل "
            "تأخیرات — برنامه‌ای که واقعاً ابزار تصمیم‌گیری باشد، نه فقط یک پیوست قرارداد."
        )
        p.offer_lede_en = (
            "From the baseline schedule to periodic updates, progress reports and delay "
            "analysis — a programme that is actually used to make decisions, not just attached "
            "to the contract."
        )
        p.offer_lede_de = (
            "Vom Basisterminplan über regelmäßige Aktualisierungen und Fortschrittsberichte bis "
            "zur Verzugsanalyse — ein Terminplan, mit dem entschieden wird, statt einer "
            "Vertragsanlage."
        )
        p.offer_body_fa = _OFFER_FA
        p.offer_body_en = _OFFER_EN
        p.offer_body_de = _OFFER_DE

        p.email = ""
        p.phone = ""
        p.telegram = ""
        p.github = ""
        p.linkedin = ""
        p.twitter = ""
        p.website = ""
        p.is_available = True

        p.save()

    # ── services: the four promises on /services/ ──────────────────────────
    def _services(self):
        rows = [
            (
                "layers",
                ("برنامه‌ی زمان‌بندی مبنا", "ساختار شکست کار، فعالیت‌ها، روابط و تقویم‌ها در Primavera P6 یا MSP — برنامه‌ای با منطق کامل و مسیر بحرانی روشن که قابل کنترل باشد."),
                ("Baseline schedule", "Work breakdown structure, activities, logic and calendars in Primavera P6 or MS Project — a fully linked programme with a clear critical path that can be controlled."),
                ("Basisterminplan", "Projektstrukturplan, Vorgänge, Abhängigkeiten und Kalender in Primavera P6 oder MS Project — ein vollständig verknüpfter Plan mit klarem kritischem Pfad."),
            ),
            (
                "clock",
                ("به‌روزرسانی و کنترل پیشرفت", "به‌روزرسانی دوره‌ای برنامه، مقایسه با برنامه‌ی مبنا، تحلیل پیشرفت و شناسایی انحراف‌ها پیش از آنکه به تأخیر تبدیل شوند."),
                ("Updates and progress control", "Periodic schedule updates, comparison against the baseline, progress analysis and deviations found before they turn into delay."),
                ("Aktualisierung und Fortschrittskontrolle", "Regelmäßige Aktualisierung, Soll-Ist-Vergleich mit dem Basisplan, Fortschrittsanalyse — Abweichungen erkennen, bevor sie zum Verzug werden."),
            ),
            (
                "target",
                ("آنالیز و لایه‌بندی تأخیرات", "تفکیک تأخیرها بر اساس علت و مسئولیت، و مستندسازی اثر هر رویداد بر تاریخ پایان — پایه‌ای روشن برای تمدید مدت و مذاکره."),
                ("Delay analysis and layering", "Delays separated by cause and responsibility, and the effect of each event on the completion date documented — a clear basis for extensions of time and negotiation."),
                ("Verzugsanalyse und -schichtung", "Verzüge nach Ursache und Verantwortung getrennt, die Wirkung jedes Ereignisses auf den Fertigstellungstermin belegt — Grundlage für Fristverlängerung und Verhandlung."),
            ),
            (
                "check",
                ("راهکار کنترلی، نه فقط گزارش", "هر گزارش با پیشنهاد اقدام همراه است: بازچینی فعالیت‌ها، موازی‌سازی یا برنامه‌ی جبرانی — با رویکرد مدیریت پروژه‌ی مبتنی بر ICB."),
                ("Corrective action, not just a report", "Every report comes with a proposed action — resequencing, fast-tracking or a recovery programme — grounded in ICB project management practice."),
                ("Maßnahmen statt nur Berichte", "Jeder Bericht enthält einen Handlungsvorschlag — Umplanung, Parallelisierung oder ein Aufholplan — auf Grundlage der ICB-Projektmanagementpraxis."),
            ),
        ]
        Service.objects.all().delete()
        for order, (icon, fa, en, de) in enumerate(rows):
            Service.objects.create(
                icon=icon,
                order=order,
                title_fa=fa[0], body_fa=fa[1],
                title_en=en[0], body_en=en[1],
                title_de=de[0], body_de=de[1],
            )

    # ── tags ──────────────────────────────────────────────────────────────
    def _tags(self) -> dict[str, Tag]:
        rows = [
            ("planning", "برنامه‌ریزی", "Planning", "Terminplanung"),
            ("project-control", "کنترل پروژه", "Project control", "Projektsteuerung"),
            ("delay-analysis", "تحلیل تأخیرات", "Delay analysis", "Verzugsanalyse"),
            ("primavera", "پریماورا", "Primavera P6", "Primavera P6"),
            ("msp", "ام‌اس‌پی", "MS Project", "MS Project"),
            ("construction-management", "مدیریت ساخت", "Construction management", "Baumanagement"),
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
        # Only what the profile states. `is_primary` marks the five things a
        # reviewer should see first: the two tools, delay analysis and
        # layering, and the certificate.
        groups = [
            (
                ("نرم‌افزارهای برنامه‌ریزی", "Scheduling software", "Planungssoftware"),
                [
                    ("Primavera P6", True),
                    ("Microsoft Project", True),
                ],
            ),
            (
                ("برنامه‌ریزی و کنترل", "Planning & control", "Planung & Steuerung"),
                [
                    ("Baseline scheduling", False),
                    ("WBS", False),
                    ("CPM / critical path", False),
                    ("Schedule updating", False),
                    ("Progress analysis", False),
                    ("Variance analysis", False),
                    ("Corrective & recovery plans", False),
                ],
            ),
            (
                ("تحلیل تأخیرات", "Delay analysis", "Verzugsanalyse"),
                [
                    ("Delay analysis", True),
                    ("Delay layering", True),
                    ("As-planned vs as-built", False),
                    ("Time impact analysis", False),
                    ("Extension of time", False),
                ],
            ),
            (
                ("مدیریت پروژه", "Project management", "Projektmanagement"),
                [
                    ("ICB Level D", True),
                    ("Construction management", False),
                    ("Project control", False),
                ],
            ),
        ]

        for gi, ((fa, en, de), skills) in enumerate(groups):
            group, _ = SkillGroup.objects.update_or_create(
                name_en=en, defaults={"name_fa": fa, "name_de": de, "order": gi}
            )
            group.skills.all().delete()
            for si, (name, primary) in enumerate(skills):
                Skill.objects.create(group=group, name=name, order=si, is_primary=primary)

    # ── projects: areas of practice ────────────────────────────────────────
    def _projects(self, tags):
        self._upsert_project(
            slug="delay-analysis",
            order=0,
            stack="Primavera P6, MS Project, As-planned vs as-built, Time impact analysis",
            tag_slugs=("delay-analysis", "project-control", "primavera"),
            tags=tags,
            fa=dict(
                title="آنالیز و لایه‌بندی تأخیرات",
                summary=(
                    "تفکیک تأخیرهای یک پروژه‌ی عمرانی بر اساس علت و مسئولیت، و سنجیدن اثر هر "
                    "رویداد بر تاریخ پایان کار."
                ),
                role="تحلیلگر تأخیرات",
                problem=_P1_PROBLEM_FA,
                body=_P1_BODY_FA,
                outcome=(
                    "گزارشی مستند که سهم هر رویداد و هر طرف از تأخیر را نشان می‌دهد و پایه‌ی "
                    "تمدید مدت یا مذاکره می‌شود."
                ),
            ),
            en=dict(
                title="Delay analysis and delay layering",
                summary=(
                    "Separating the delays on a civil engineering project by cause and "
                    "responsibility, and measuring what each event did to the completion date."
                ),
                role="Delay analyst",
                problem=_P1_PROBLEM_EN,
                body=_P1_BODY_EN,
                outcome=(
                    "A documented report showing each event's and each party's share of the "
                    "delay — a basis for an extension of time or a negotiation."
                ),
            ),
            de=dict(
                title="Verzugsanalyse und Verzugsschichtung",
                summary=(
                    "Verzüge eines Bauprojekts nach Ursache und Verantwortung trennen und "
                    "messen, was jedes Ereignis am Fertigstellungstermin verändert hat."
                ),
                role="Verzugsanalyse",
                problem=_P1_PROBLEM_DE,
                body=_P1_BODY_DE,
                outcome=(
                    "Ein belegter Bericht zum Anteil jedes Ereignisses und jeder Partei am "
                    "Verzug — Grundlage für Fristverlängerung oder Verhandlung."
                ),
            ),
        )

        self._upsert_project(
            slug="baseline-schedule",
            order=1,
            stack="Primavera P6, MS Project, WBS, CPM",
            tag_slugs=("planning", "primavera", "msp"),
            tags=tags,
            fa=dict(
                title="تهیه‌ی برنامه‌ی زمان‌بندی مبنا",
                summary=(
                    "از ساختار شکست کار تا مسیر بحرانی: برنامه‌ای در Primavera P6 یا MSP که منطق "
                    "کامل دارد و می‌شود با آن پروژه را کنترل کرد."
                ),
                role="برنامه‌ریز پروژه",
                problem=_P2_PROBLEM_FA,
                body=_P2_BODY_FA,
                outcome=(
                    "برنامه‌ی مبنایی با روابط کامل، تقویم‌های درست و مسیر بحرانی روشن — مرجع "
                    "همه‌ی مقایسه‌های بعدی."
                ),
            ),
            en=dict(
                title="Building the baseline schedule",
                summary=(
                    "From the work breakdown structure to the critical path: a programme in "
                    "Primavera P6 or MS Project with complete logic that a project can be "
                    "controlled against."
                ),
                role="Project planner",
                problem=_P2_PROBLEM_EN,
                body=_P2_BODY_EN,
                outcome=(
                    "A baseline with complete logic, correct calendars and a clear critical path "
                    "— the reference for every comparison that follows."
                ),
            ),
            de=dict(
                title="Erstellung des Basisterminplans",
                summary=(
                    "Vom Projektstrukturplan bis zum kritischen Pfad: ein Terminplan in "
                    "Primavera P6 oder MS Project mit vollständiger Logik, an dem sich ein "
                    "Projekt steuern lässt."
                ),
                role="Terminplanung",
                problem=_P2_PROBLEM_DE,
                body=_P2_BODY_DE,
                outcome=(
                    "Ein Basisplan mit vollständiger Logik, korrekten Kalendern und klarem "
                    "kritischem Pfad — die Referenz für jeden späteren Vergleich."
                ),
            ),
        )

        self._upsert_project(
            slug="progress-control",
            order=2,
            stack="Primavera P6, MS Project, Baseline comparison, Progress analysis",
            tag_slugs=("project-control", "planning", "construction-management"),
            tags=tags,
            fa=dict(
                title="به‌روزرسانی برنامه و کنترل پیشرفت",
                summary=(
                    "به‌روزرسانی دوره‌ای برنامه، مقایسه با مبنا، شناسایی انحراف‌ها و پیشنهاد "
                    "راهکار کنترلی پیش از آنکه دیر شود."
                ),
                role="کارشناس کنترل پروژه",
                problem=_P3_PROBLEM_FA,
                body=_P3_BODY_FA,
                outcome=(
                    "گزارش دوره‌ای که انحراف را با علتش نشان می‌دهد و برای هر کدام یک اقدام "
                    "مشخص پیشنهاد می‌کند."
                ),
            ),
            en=dict(
                title="Schedule updates and progress control",
                summary=(
                    "Periodic updates, comparison against the baseline, deviations found and a "
                    "corrective action proposed while there is still time to act."
                ),
                role="Project control",
                problem=_P3_PROBLEM_EN,
                body=_P3_BODY_EN,
                outcome=(
                    "A periodic report that shows each deviation with its cause and proposes a "
                    "concrete action for it."
                ),
            ),
            de=dict(
                title="Terminaktualisierung und Fortschrittskontrolle",
                summary=(
                    "Regelmäßige Aktualisierung, Soll-Ist-Vergleich mit dem Basisplan, "
                    "Abweichungen erkennen und eine Maßnahme vorschlagen, solange noch Zeit ist."
                ),
                role="Projektsteuerung",
                problem=_P3_PROBLEM_DE,
                body=_P3_BODY_DE,
                outcome=(
                    "Ein regelmäßiger Bericht, der jede Abweichung mit ihrer Ursache zeigt und "
                    "eine konkrete Maßnahme vorschlägt."
                ),
            ),
        )

        self._upsert_project(
            slug="project-management-icb",
            order=3,
            stack="ICB Level D, Construction management",
            tag_slugs=("construction-management", "project-control"),
            tags=tags,
            featured=False,
            fa=dict(
                title="مدیریت پروژه با رویکرد ICB",
                summary=(
                    "برنامه‌ریزی و کنترل به‌عنوان بخشی از مدیریت پروژه، نه یک کار جدا — بر پایه‌ی "
                    "گواهینامه‌ی ICB Level D و تحصیل در مدیریت ساخت."
                ),
                role="مدیریت پروژه",
                problem=_P4_PROBLEM_FA,
                body=_P4_BODY_FA,
                outcome=(
                    "برنامه‌ای که به قرارداد، منابع و ذی‌نفعان پروژه گره خورده است، نه فقط به "
                    "نمودار گانت."
                ),
            ),
            en=dict(
                title="Project management the ICB way",
                summary=(
                    "Planning and control as part of managing a project rather than a separate "
                    "task — grounded in the ICB Level D certificate and a degree in construction "
                    "management."
                ),
                role="Project management",
                problem=_P4_PROBLEM_EN,
                body=_P4_BODY_EN,
                outcome=(
                    "A programme tied to the contract, the resources and the stakeholders of the "
                    "project, not only to a Gantt chart."
                ),
            ),
            de=dict(
                title="Projektmanagement nach ICB",
                summary=(
                    "Planung und Steuerung als Teil des Projektmanagements statt als "
                    "Einzelaufgabe — auf Grundlage des Zertifikats ICB Level D und eines "
                    "Studiums im Baumanagement."
                ),
                role="Projektmanagement",
                problem=_P4_PROBLEM_DE,
                body=_P4_BODY_DE,
                outcome=(
                    "Ein Terminplan, der mit Vertrag, Ressourcen und Beteiligten verbunden ist — "
                    "nicht nur mit einem Gantt-Diagramm."
                ),
            ),
        )

    def _upsert_project(
        self, *, slug, order, stack, tag_slugs, tags, fa, en, de, year=None, demo_url="", featured=True
    ):
        # `featured` is what the home page shows, and it shows three: the
        # three core practices. The fourth lives on /projects.
        defaults = {
            "year": year,
            "order": order,
            "stack": stack,
            "demo_url": demo_url,
            "is_featured": featured,
            "is_published": True,
        }
        for code, values in (("fa", fa), ("en", en), ("de", de)):
            for field, value in values.items():
                defaults[f"{field}_{code}"] = value
        project, _ = Project.objects.update_or_create(slug=slug, defaults=defaults)
        project.tags.set([tags[s] for s in tag_slugs])


# ── long copy ──────────────────────────────────────────────────────────────
# Kept at the bottom so the command reads as structure, not as prose.

# ── the services page ──────────────────────────────────────────────────────
_OFFER_FA = """\
### چه کارهایی انجام می‌دهم

- **تهیه‌ی برنامه‌ی زمان‌بندی** در Primavera P6 یا Microsoft Project — ساختار شکست
  کار، فعالیت‌ها، روابط، تقویم‌ها و مسیر بحرانی.
- **کنترل و به‌روزرسانی برنامه** در دوره‌های منظم، همراه با تحلیل پیشرفت و مقایسه
  با برنامه‌ی مبنا.
- **شناسایی انحراف‌ها و ارائه‌ی راهکار کنترلی** — بازچینی فعالیت‌ها، موازی‌سازی یا
  برنامه‌ی جبرانی.
- **آنالیز و لایه‌بندی تأخیرات** — تفکیک تأخیرها بر اساس علت و مسئولیت و مستندسازی
  اثرشان بر تاریخ پایان پروژه.

### یک همکاری چطور پیش می‌رود

1. **آشنایی با پروژه** — قرارداد، دامنه‌ی کار، برنامه‌ی موجود و وضعیت فعلی.
2. **توافق بر خروجی‌ها** — چه برنامه‌ای، چه گزارشی و در چه دوره‌هایی.
3. **تهیه یا بازبینی برنامه** — و تأیید آن به‌عنوان مبنای کنترل.
4. **کنترل مستمر** — به‌روزرسانی، گزارش و پیشنهاد اقدام در هر دوره.
"""

_OFFER_EN = """\
### What I do

- **Schedule preparation** in Primavera P6 or Microsoft Project — work breakdown
  structure, activities, logic, calendars and the critical path.
- **Schedule control and updates** at regular intervals, with progress analysis
  and comparison against the baseline.
- **Deviations found and corrective action proposed** — resequencing,
  fast-tracking or a recovery programme.
- **Delay analysis and delay layering** — delays separated by cause and
  responsibility, and their effect on the completion date documented.

### How an engagement runs

1. **Getting to know the project** — the contract, the scope, the existing
   programme and where things stand.
2. **Agreeing the deliverables** — which programme, which reports, how often.
3. **Preparing or reviewing the programme** — and approving it as the baseline.
4. **Continuous control** — an update, a report and a proposed action every period.
"""

_OFFER_DE = """\
### Was ich übernehme

- **Terminplanung** in Primavera P6 oder Microsoft Project — Projektstrukturplan,
  Vorgänge, Abhängigkeiten, Kalender und kritischer Pfad.
- **Terminsteuerung und Aktualisierung** in festen Abständen, mit
  Fortschrittsanalyse und Soll-Ist-Vergleich zum Basisplan.
- **Abweichungen erkennen und Maßnahmen vorschlagen** — Umplanung,
  Parallelisierung oder ein Aufholplan.
- **Verzugsanalyse und Verzugsschichtung** — Verzüge nach Ursache und
  Verantwortung getrennt, ihre Wirkung auf den Fertigstellungstermin belegt.

### So läuft eine Zusammenarbeit ab

1. **Das Projekt kennenlernen** — Vertrag, Leistungsumfang, vorhandener
   Terminplan und aktueller Stand.
2. **Ergebnisse vereinbaren** — welcher Plan, welche Berichte, in welchem Takt.
3. **Terminplan erstellen oder prüfen** — und als Basis freigeben.
4. **Laufende Steuerung** — in jeder Periode Aktualisierung, Bericht und
   Maßnahmenvorschlag.
"""

# ── biography ──────────────────────────────────────────────────────────────
_BIO_FA = """\
کارشناس ارشد مهندسی عمران در گرایش مدیریت ساخت از دانشگاه علم و صنعت ایران هستم،
با دانش تخصصی و مهارت در برنامه‌ریزی، کنترل پروژه و مدیریت زمان‌بندی پروژه‌های
عمرانی.

### توانمندی‌های تخصصی

- تسلط کامل بر **Microsoft Project (MSP)**
- تسلط بر **Primavera P6**
- دارای گواهینامه‌ی **ICB Level D** در مدیریت پروژه
- مسلط به **آنالیز و لایه‌بندی تأخیرات** (Delay Analysis)
- توانمند در **تهیه، کنترل و به‌روزرسانی برنامه‌ی زمان‌بندی** پروژه، تحلیل پیشرفت،
  شناسایی انحرافات و ارائه‌ی راهکارهای کنترلی

### رویکرد

برنامه‌ی زمان‌بندی برای من ابزار تصمیم‌گیری است، نه یک مدرک. برنامه‌ای که منطقش
کامل باشد، مرتب به‌روز شود و انحراف‌ها را زود نشان دهد، به مدیر پروژه فرصت می‌دهد
پیش از تأخیر اقدام کند — و اگر تأخیری رخ داد، روشن می‌کند از کجا آمده و سهم هر
طرف چقدر است. در این کار رویکردم دقیق، تحلیلی و نتیجه‌محور است.

### حوزه‌ی علاقه

برنامه‌ریزی و کنترل پروژه، مدیریت ساخت و تحلیل تأخیرات پروژه‌های عمرانی.
"""

_BIO_EN = """\
I hold an MSc in civil engineering, specialising in construction management, from
Iran University of Science and Technology, with specialist knowledge and skill in
planning, project control and schedule management for civil engineering
projects.

### Core capabilities

- Full command of **Microsoft Project (MSP)**
- Command of **Primavera P6**
- **ICB Level D** certificate in project management
- Skilled in **delay analysis and delay layering**
- Able to **prepare, control and update project schedules**, analyse progress,
  identify deviations and propose corrective action

### Approach

To me a schedule is a tool for making decisions, not a document to file. A
programme with complete logic, updated regularly and showing deviations early,
gives a project manager time to act before a delay — and when a delay does
happen, it shows where it came from and what each party's share of it is. My
approach to the work is precise, analytical and focused on results.

### Where I want to work

Project planning and control, construction management, and delay analysis on
civil engineering projects.
"""

_BIO_DE = """\
Ich habe einen M.Sc. im Bauingenieurwesen mit Schwerpunkt Baumanagement von der
Iran University of Science and Technology und verfüge über Fachwissen und
Erfahrung in Planung, Projektsteuerung und Terminmanagement von Bauprojekten.

### Kernkompetenzen

- Umfassende Beherrschung von **Microsoft Project (MSP)**
- Sicherer Umgang mit **Primavera P6**
- Zertifikat **ICB Level D** im Projektmanagement
- Versiert in **Verzugsanalyse und Verzugsschichtung** (Delay Analysis)
- **Erstellung, Steuerung und Aktualisierung von Terminplänen**, Fortschrittsanalyse,
  Erkennen von Abweichungen und Vorschlag von Steuerungsmaßnahmen

### Arbeitsweise

Ein Terminplan ist für mich ein Entscheidungswerkzeug, kein Ablagedokument. Ein
Plan mit vollständiger Logik, der regelmäßig aktualisiert wird und Abweichungen
früh zeigt, gibt der Projektleitung Zeit zu handeln, bevor ein Verzug entsteht —
und wenn doch einer entsteht, zeigt er, woher er kommt und welcher Anteil auf
welche Partei entfällt. Ich arbeite genau, analytisch und ergebnisorientiert.

### Wo ich arbeiten möchte

Projektplanung und -steuerung, Baumanagement und Verzugsanalyse im Bauwesen.
"""

# ── practice 1: delay analysis ─────────────────────────────────────────────
_P1_PROBLEM_FA = """\
در یک پروژه‌ی عمرانی تأخیر تقریباً هیچ‌وقت یک علت ندارد. تأخیر در تحویل زمین یا
نقشه، تغییر دستور کار، کمبود منابع پیمانکار و شرایط پیش‌بینی‌نشده روی هم
می‌افتند، و بدون تحلیل، هر طرف کل تأخیر را به گردن دیگری می‌اندازد.
"""

_P1_BODY_FA = """\
### روش کار

- **برنامه‌ی مبنا و برنامه‌ی واقعی کنار هم** — آنچه قرار بود و آنچه رخ داد، فعالیت
  به فعالیت.
- **فهرست رویدادهای تأخیرزا** از مکاتبات، صورت‌جلسات و گزارش‌های روزانه، هر کدام با
  تاریخ و مستند.
- **سنجیدن اثر هر رویداد بر مسیر بحرانی** — تأخیری که به مسیر بحرانی نرسد، تاریخ
  پایان را جابه‌جا نمی‌کند.
- **لایه‌بندی تأخیرات** — تفکیک بر اساس مسئولیت (کارفرما، پیمانکار، عوامل خارج از
  کنترل دو طرف) و شناسایی تأخیرهای هم‌زمان.

### خروجی

گزارشی که با زبان برنامه‌ی زمان‌بندی و مستندات پروژه نشان می‌دهد هر رویداد چند روز
به پروژه اضافه کرده و این روزها به چه کسی برمی‌گردد.
"""

_P1_PROBLEM_EN = """\
On a civil engineering project a delay almost never has a single cause. Late
access to the site or to drawings, change orders, a contractor short of
resources and unforeseen conditions overlap — and without an analysis each party
blames the whole delay on the other.
"""

_P1_BODY_EN = """\
### How the work is done

- **The baseline and the as-built side by side** — what was planned and what
  happened, activity by activity.
- **A register of delay events** built from correspondence, minutes and daily
  reports, each one dated and documented.
- **Each event measured against the critical path** — a delay that never
  reaches the critical path does not move the completion date.
- **Delay layering** — delays separated by responsibility (employer,
  contractor, events outside either party's control), with concurrent delays
  identified.

### The deliverable

A report that shows, in the language of the programme and the project records,
how many days each event added and to whom those days belong.
"""

_P1_PROBLEM_DE = """\
Bei einem Bauprojekt hat ein Verzug fast nie nur eine Ursache. Verspätete
Übergabe des Baufelds oder der Pläne, Änderungsanordnungen, fehlende Ressourcen
des Auftragnehmers und unvorhergesehene Umstände überlagern sich — und ohne
Analyse schiebt jede Seite den ganzen Verzug der anderen zu.
"""

_P1_BODY_DE = """\
### Vorgehen

- **Basisplan und Ist-Ablauf nebeneinander** — was geplant war und was geschah,
  Vorgang für Vorgang.
- **Ein Register der Verzugsereignisse** aus Schriftverkehr, Protokollen und
  Bautagesberichten, jedes datiert und belegt.
- **Jedes Ereignis am kritischen Pfad gemessen** — ein Verzug, der den
  kritischen Pfad nie erreicht, verschiebt den Fertigstellungstermin nicht.
- **Verzugsschichtung** — Trennung nach Verantwortung (Auftraggeber,
  Auftragnehmer, von keiner Seite beherrschbare Ereignisse) und Erkennen
  paralleler Verzüge.

### Ergebnis

Ein Bericht, der in der Sprache des Terminplans und der Projektunterlagen zeigt,
wie viele Tage jedes Ereignis hinzugefügt hat und wem diese Tage zuzurechnen sind.
"""

# ── practice 2: the baseline schedule ─────────────────────────────────────
_P2_PROBLEM_FA = """\
برنامه‌ای که روابط ناقص، قیدهای اجباری یا فعالیت‌های بی‌سرانجام دارد، روی کاغذ
درست به نظر می‌رسد اما با اولین به‌روزرسانی از هم می‌پاشد و مسیر بحرانی‌اش معنایی
ندارد.
"""

_P2_BODY_FA = """\
### روش کار

- **ساختار شکست کار (WBS)** هماهنگ با دامنه‌ی قرارداد و شیوه‌ی اجرای پروژه.
- **فعالیت‌ها و روابط** — هر فعالیت پیش‌نیاز و پس‌نیاز دارد و قید اجباری فقط جایی
  که قرارداد می‌خواهد.
- **تقویم‌ها و مدت‌ها** — روزهای کاری، تعطیلات و محدودیت‌های فصلی.
- **مسیر بحرانی و شناوری‌ها** — بررسی اینکه مسیر بحرانی منطقی است و شناوری‌ها
  واقعی‌اند.
- **اجرا در Primavera P6 یا Microsoft Project**، هر کدام که پروژه و کارفرما نیاز
  دارند.
"""

_P2_PROBLEM_EN = """\
A programme with missing logic, hard constraints or open-ended activities looks
right on paper, then falls apart at the first update — and its critical path
means nothing.
"""

_P2_BODY_EN = """\
### How the work is done

- **A work breakdown structure** aligned with the contract scope and the way the
  project will be built.
- **Activities and logic** — every activity has a predecessor and a successor,
  and hard constraints only where the contract demands them.
- **Calendars and durations** — working days, holidays and seasonal limits.
- **Critical path and float** — checking that the critical path makes sense and
  the float is real.
- **Built in Primavera P6 or Microsoft Project**, whichever the project and the
  client need.
"""

_P2_PROBLEM_DE = """\
Ein Terminplan mit fehlenden Abhängigkeiten, harten Zwangsterminen oder offenen
Vorgängen sieht auf dem Papier richtig aus, zerfällt aber bei der ersten
Aktualisierung — und sein kritischer Pfad bedeutet nichts.
"""

_P2_BODY_DE = """\
### Vorgehen

- **Ein Projektstrukturplan**, abgestimmt auf den Leistungsumfang und die Art,
  wie gebaut wird.
- **Vorgänge und Abhängigkeiten** — jeder Vorgang hat Vorgänger und Nachfolger,
  harte Termine nur dort, wo der Vertrag sie verlangt.
- **Kalender und Dauern** — Arbeitstage, Feiertage und jahreszeitliche Grenzen.
- **Kritischer Pfad und Puffer** — prüfen, ob der kritische Pfad schlüssig und
  die Puffer echt sind.
- **Umsetzung in Primavera P6 oder Microsoft Project**, je nachdem, was Projekt
  und Auftraggeber brauchen.
"""

# ── practice 3: updates and progress control ──────────────────────────────
_P3_PROBLEM_FA = """\
برنامه‌ای که بعد از تصویب دیگر به‌روز نمی‌شود، چند ماه بعد فقط یک سند تاریخی است؛
انحراف‌ها وقتی دیده می‌شوند که جبرانشان دیگر ممکن نیست.
"""

_P3_BODY_FA = """\
### روش کار

- **به‌روزرسانی دوره‌ای** — ثبت درصد پیشرفت، تاریخ‌های واقعی شروع و پایان و مدت
  باقی‌مانده‌ی هر فعالیت.
- **مقایسه با برنامه‌ی مبنا** — کجا جلوتریم، کجا عقب‌تر، و مسیر بحرانی چطور جابه‌جا
  شده است.
- **تحلیل پیشرفت** — پیشرفت برنامه‌ای در برابر پیشرفت واقعی، برای کل پروژه و هر
  بخش آن.
- **شناسایی انحراف و علتش** — و پیشنهاد اقدام: بازچینی، موازی‌سازی، افزایش منابع یا
  برنامه‌ی جبرانی.
"""

_P3_PROBLEM_EN = """\
A programme that stops being updated once it is approved is, a few months later,
a historical document — deviations become visible only when it is too late to
recover them.
"""

_P3_BODY_EN = """\
### How the work is done

- **Periodic updates** — percent complete, actual start and finish dates and the
  remaining duration of every activity.
- **Comparison against the baseline** — where the project is ahead, where it is
  behind, and how the critical path has moved.
- **Progress analysis** — planned against actual progress, for the whole project
  and for each part of it.
- **Each deviation and its cause** — with a proposed action: resequencing,
  fast-tracking, more resources or a recovery programme.
"""

_P3_PROBLEM_DE = """\
Ein Terminplan, der nach der Freigabe nicht mehr aktualisiert wird, ist ein paar
Monate später ein historisches Dokument — Abweichungen werden erst sichtbar, wenn
sie sich nicht mehr aufholen lassen.
"""

_P3_BODY_DE = """\
### Vorgehen

- **Regelmäßige Aktualisierung** — Fertigstellungsgrad, tatsächliche Anfangs- und
  Endtermine und Restdauer jedes Vorgangs.
- **Soll-Ist-Vergleich mit dem Basisplan** — wo das Projekt vorn liegt, wo es
  zurückliegt und wie sich der kritische Pfad verschoben hat.
- **Fortschrittsanalyse** — geplanter gegenüber tatsächlichem Fortschritt, für das
  ganze Projekt und jeden Teil.
- **Jede Abweichung mit ihrer Ursache** — und ein Maßnahmenvorschlag: Umplanung,
  Parallelisierung, mehr Ressourcen oder ein Aufholplan.
"""

# ── practice 4: project management ────────────────────────────────────────
_P4_PROBLEM_FA = """\
زمان‌بندی جدا از بقیه‌ی پروژه معنا ندارد: قرارداد، منابع، هزینه، ریسک و
ذی‌نفعان همه روی برنامه اثر می‌گذارند و برنامه هم روی همه‌ی آن‌ها.
"""

_P4_BODY_FA = """\
### پشتوانه

- **گواهینامه‌ی ICB Level D** — چارچوب بین‌المللی شایستگی‌های مدیریت پروژه.
- **کارشناسی ارشد مدیریت ساخت** از دانشگاه علم و صنعت ایران.

### در عمل

برنامه‌ریزی و کنترل را در کنار مدیریت قرارداد، منابع و ارتباط با ذی‌نفعان می‌بینم؛
گزارشی که برای تصمیم‌گیری مدیر پروژه نوشته شود، نه فقط برای بایگانی.
"""

_P4_PROBLEM_EN = """\
A schedule means nothing on its own: the contract, the resources, the cost, the
risks and the stakeholders all act on the programme, and the programme acts on
all of them.
"""

_P4_BODY_EN = """\
### The grounding

- **The ICB Level D certificate** — the international framework of project
  management competences.
- **An MSc in construction management** from Iran University of Science and
  Technology.

### In practice

I see planning and control alongside contract management, resources and the
people with a stake in the project — a report written for the project manager's
next decision, not for the archive.
"""

_P4_PROBLEM_DE = """\
Ein Terminplan hat für sich allein keine Bedeutung: Vertrag, Ressourcen, Kosten,
Risiken und Beteiligte wirken auf den Plan ein — und der Plan auf sie alle.
"""

_P4_BODY_DE = """\
### Grundlage

- **Das Zertifikat ICB Level D** — der internationale Rahmen der
  Projektmanagement-Kompetenzen.
- **Ein M.Sc. im Baumanagement** von der Iran University of Science and
  Technology.

### In der Praxis

Planung und Steuerung sehe ich zusammen mit Vertragsmanagement, Ressourcen und
den Beteiligten — ein Bericht für die nächste Entscheidung der Projektleitung,
nicht für das Archiv.
"""
