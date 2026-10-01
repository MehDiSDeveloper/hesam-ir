"""
Seed the first two articles, in fa/en/de, so /articles/ is not empty.

    python manage.py seed_articles            # create the ones that are missing
    python manage.py seed_articles --update   # also overwrite them with this text

Both are explainers of method, written for this site: no venue, no DOI, no
co-authors, and — like seed_profile — no project, employer or figure is named.
The standards they cite (SCL Protocol, AACE RP 29R-03, the DCMA 14-point
assessment) are public documents.

Without --update an article edited in the admin is left alone, so running this
again on a live database is harmless.
"""

import datetime as dt

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.content.models import Article, Tag

TAGS = {
    "delay-analysis": ("تحلیل تأخیرات", "Delay analysis", "Verzugsanalyse"),
    "planning": ("برنامه‌ریزی", "Planning", "Terminplanung"),
    "project-control": ("کنترل پروژه", "Project control", "Projektsteuerung"),
    "primavera": ("پریماورا", "Primavera P6", "Primavera P6"),
}


DELAY_FA = """\
وقتی پروژه‌ای از موعد قراردادی عقب می‌افتد، سؤال اصلی ساده است: **چند روز، به خاطر چه، و به عهده‌ی چه کسی؟** جواب دادن به آن ساده نیست، و روشی که برای تحلیل انتخاب می‌شود تقریباً به همان اندازه‌ی خود داده‌ها در نتیجه اثر دارد.

## روش‌های اصلی

**برنامه‌ی تأثیریافته (Impacted As-Planned):** رویدادهای تأخیر به صورت قطعه‌برنامه (fragnet) به برنامه‌ی مبنا اضافه می‌شوند و جابه‌جایی تاریخ پایان اندازه‌گیری می‌شود. سریع و کم‌هزینه است، اما آنچه واقعاً در کارگاه رخ داده را نادیده می‌گیرد.

**تحلیل اثر زمانی (Time Impact Analysis):** هر رویداد در آخرین برنامه‌ی به‌روزشده‌ی پیش از وقوعش وارد می‌شود. پروتکل SCL این روش را برای ارزیابی هم‌زمان تمدید مدت ترجیح می‌دهد، چون وضعیت واقعی پروژه در همان لحظه را در نظر می‌گیرد.

**تحلیل پنجره‌ای (Windows / Time Slice):** دوره‌ی اجرا به پنجره‌هایی بین به‌روزرسانی‌های متوالی تقسیم می‌شود و در هر پنجره مسیر بحرانی و تأخیر آن بررسی می‌شود. به برنامه‌های به‌روزشده‌ی منظم و قابل‌اعتماد نیاز دارد.

**مقایسه‌ی برنامه با اجرا (As-Planned vs As-Built):** برنامه‌ی مبنا با آنچه اجرا شده مقایسه می‌شود. وقتی برنامه‌ی زمان‌بندی خوبی در دست نیست کاربرد دارد، اما تشخیص مسیر بحرانی در آن بیشتر به قضاوت متکی است.

**برنامه‌ی اجراشده‌ی فروریخته (Collapsed As-Built):** تأخیرها از برنامه‌ی اجراشده حذف می‌شوند تا معلوم شود «اگر این رویداد نبود» پروژه کی تمام می‌شد. به یک برنامه‌ی اجرایی دقیق با منطق کامل نیاز دارد.

## انتخاب روش

روش درست را پنج چیز تعیین می‌کند:

1. **قرارداد** — اگر روشی را مشخص کرده، همان اولویت دارد.
2. **زمان تحلیل** — پیش از وقوع (برآورد) یا پس از آن (بازسازی).
3. **سوابق موجود** — کیفیت برنامه‌ی مبنا، به‌روزرسانی‌ها، گزارش‌های روزانه.
4. **ماهیت اختلاف** — چند رویداد محدود یا ده‌ها رویداد هم‌پوشان.
5. **تناسب** — هزینه‌ی تحلیل باید با اهمیت ادعا متناسب باشد.

## تأخیر هم‌زمان

سخت‌ترین بخش اغلب جایی است که تأخیر کارفرما و پیمانکار هم‌زمان بر مسیر بحرانی اثر گذاشته‌اند. اینجا لایه‌بندی تأخیرات (delay layering) — جدا کردن اثر هر رویداد و ترتیب آن‌ها — تفاوت یک ادعای قابل‌دفاع با یک عدد بحث‌برانگیز است.

هیچ روشی «بهترین» نیست؛ روشی بهتر است که با سوابق موجود قابل پشتیبانی باشد و طرف مقابل بتواند گام‌به‌گام آن را دنبال کند.
"""

DELAY_EN = """\
When a project finishes later than the contract says, the question is simple: **how many days, caused by what, and whose risk were they?** Answering it is not, and the method chosen shapes the result almost as much as the facts do.

## The main methods

**Impacted As-Planned.** Delay events are added to the baseline as fragnets and the movement of the finish date is measured. Quick and cheap, but it ignores what actually happened on site.

**Time Impact Analysis.** Each event is inserted into the last schedule update before it occurred. The SCL Protocol prefers it for contemporaneous extension-of-time assessment because it works from the project's real status at that moment.

**Windows / Time Slice Analysis.** The job is divided into windows between successive updates, and the critical path and its slippage are examined in each. It needs regular, reliable updates.

**As-Planned vs As-Built.** The baseline is compared with what was built. Useful when no good schedule exists, but identifying the critical path leans more on judgement.

**Collapsed As-Built.** Delays are taken out of the as-built schedule to show when the project would have finished "but for" them. It needs a detailed as-built schedule with complete logic.

## Choosing one

Five things decide the right method:

1. **The contract** — if it names a method, that comes first.
2. **Timing** — before the delay has played out (forecast) or after it (reconstruction).
3. **The records** — quality of the baseline, the updates, the daily reports.
4. **The dispute** — a handful of events, or dozens overlapping.
5. **Proportionality** — the cost of the analysis should fit what is at stake.

## Concurrent delay

The hardest part is usually where employer and contractor delays hit the critical path at the same time. Delay layering — separating each event's effect and its sequence — is what turns a debatable number into a defensible claim.

No method is "best". The better one is the method the records can support and the other side can follow step by step.
"""

DELAY_DE = """\
Wenn ein Projekt später fertig wird als vertraglich vereinbart, ist die Frage einfach: **wie viele Tage, wodurch verursacht, und in wessen Risikosphäre?** Die Antwort ist es nicht — und die gewählte Methode prägt das Ergebnis fast so stark wie die Fakten.

## Die wichtigsten Methoden

**Impacted As-Planned.** Störungsereignisse werden als Fragnets in den Basisterminplan eingefügt, gemessen wird die Verschiebung des Endtermins. Schnell und günstig, blendet aber aus, was auf der Baustelle tatsächlich geschah.

**Time Impact Analysis.** Jedes Ereignis wird in die letzte Terminplanfortschreibung vor seinem Eintreten eingefügt. Das SCL Protocol bevorzugt sie für die zeitnahe Bewertung von Bauzeitverlängerungen, weil sie vom realen Projektstand ausgeht.

**Windows- / Time-Slice-Analyse.** Die Bauzeit wird in Fenster zwischen aufeinanderfolgenden Fortschreibungen geteilt; in jedem wird der kritische Weg und sein Verzug untersucht. Sie setzt regelmäßige, verlässliche Fortschreibungen voraus.

**Soll-Ist-Vergleich (As-Planned vs As-Built).** Der Basisplan wird mit dem tatsächlichen Ablauf verglichen. Nützlich, wenn kein guter Terminplan vorliegt; die Bestimmung des kritischen Wegs stützt sich aber stärker auf Einschätzung.

**Collapsed As-Built.** Verzögerungen werden aus dem Ist-Terminplan herausgenommen, um zu zeigen, wann das Projekt ohne sie fertig geworden wäre. Erfordert einen detaillierten Ist-Plan mit vollständiger Logik.

## Die Wahl der Methode

Fünf Dinge entscheiden:

1. **Der Vertrag** — schreibt er eine Methode vor, hat sie Vorrang.
2. **Der Zeitpunkt** — vor dem Auswirken der Störung (Prognose) oder danach (Rekonstruktion).
3. **Die Unterlagen** — Qualität des Basisplans, der Fortschreibungen, der Bautagesberichte.
4. **Der Streitgegenstand** — wenige Ereignisse oder Dutzende, die sich überlagern.
5. **Verhältnismäßigkeit** — der Aufwand der Analyse muss zum Streitwert passen.

## Parallele Verzögerungen

Am schwierigsten ist meist der Fall, in dem Verzögerungen von Auftraggeber und Auftragnehmer gleichzeitig den kritischen Weg treffen. Delay Layering — die Wirkung und Abfolge jedes Ereignisses zu trennen — macht aus einer strittigen Zahl einen belastbaren Anspruch.

Keine Methode ist „die beste“. Besser ist die, die sich mit den vorhandenen Unterlagen belegen lässt und die die Gegenseite Schritt für Schritt nachvollziehen kann.
"""


BASELINE_FA = """\
برنامه‌ی مبنا (baseline) معیاری است که تمام پیشرفت و تأخیرهای بعدی با آن سنجیده می‌شوند. اگر منطقش ناقص باشد، هر گزارش پیشرفت و هر تحلیل تأخیر بعدی روی زمین سستی بنا شده است. ارزیابی ۱۴ نقطه‌ای DCMA یک چک‌لیست شناخته‌شده برای سنجش کیفیت آن است؛ مهم‌ترین نکاتش این‌هاست.

## منطق

- **فعالیت بدون پیش‌نیاز یا پس‌نیاز:** جز شروع و پایان پروژه، هر فعالیت باید در شبکه گره خورده باشد. سقف پیشنهادی: ۵٪.
- **Lead (تأخیر منفی):** نباید وجود داشته باشد؛ رابطه‌ی شفاف‌تری را پنهان می‌کند.
- **Lag:** حداکثر ۵٪ روابط. زمان انتظار واقعی (مثل عمل‌آوری بتن) بهتر است فعالیت جداگانه باشد.
- **نوع رابطه:** دست‌کم ۹۰٪ روابط از نوع پایان‌به‌شروع (FS) باشند.

## قیدها و شناوری

- **قید سخت (Must Start/Finish On):** حداکثر ۵٪. قید سخت منطق را قطع می‌کند و مسیر بحرانی را مصنوعی می‌سازد.
- **شناوری زیاد:** فعالیت‌هایی با شناوری کل بیش از ۴۴ روز کاری معمولاً نشانه‌ی رابطه‌ی جاافتاده‌اند؛ حداکثر ۵٪.
- **شناوری منفی:** در برنامه‌ی مبنا نباید وجود داشته باشد.

## مدت و منابع

- **مدت طولانی:** فعالیت‌های بالای ۴۴ روز کاری حداکثر ۵٪ باشند؛ فعالیت بلند را نمی‌توان به‌خوبی کنترل کرد.
- **تاریخ‌های نامعتبر:** تاریخ واقعی در آینده یا تاریخ پیش‌بینی در گذشته، خطای به‌روزرسانی است.
- **منابع:** فعالیت‌ها باید منابع یا هزینه داشته باشند تا برنامه با برآورد هزینه هم‌خوان باشد.

## آزمون‌های عملکرد

- **آزمون مسیر بحرانی:** اگر به یک فعالیت بحرانی تأخیر مصنوعی بدهید، تاریخ پایان باید به همان اندازه جابه‌جا شود.
- **CPLI** و **BEI:** شاخص طول مسیر بحرانی و شاخص اجرای برنامه — هر دو دست‌کم ۰٫۹۵.

این عددها قانون نیستند؛ آستانه‌هایی‌اند که نشان می‌دهند کجا باید دقیق‌تر نگاه کرد. برنامه‌ای که از این آزمون‌ها بگذرد، هم برای کنترل پروژه قابل‌اتکاست و هم در زمان تحلیل تأخیر قابل‌دفاع.
"""

BASELINE_EN = """\
The baseline is the yardstick every later progress report and delay claim is measured against. If its logic is weak, everything built on it inherits the weakness. The DCMA 14-point assessment is a widely used checklist for testing one; these are the checks that matter most.

## Logic

- **Missing predecessors or successors:** apart from the project start and finish, every activity should be tied into the network. Threshold: 5%.
- **Leads (negative lags):** none. They hide a relationship that should be stated plainly.
- **Lags:** at most 5% of relationships. Real waiting time, such as concrete curing, is better modelled as its own activity.
- **Relationship types:** at least 90% finish-to-start.

## Constraints and float

- **Hard constraints (Must Start/Finish On):** at most 5%. A hard constraint cuts the logic and makes the critical path artificial.
- **High float:** activities with more than 44 working days of total float usually point to a missing link; at most 5%.
- **Negative float:** none in a baseline.

## Durations and resources

- **High duration:** at most 5% of activities over 44 working days — a long activity cannot be controlled well.
- **Invalid dates:** an actual date in the future or a forecast in the past is an update error.
- **Resources:** activities should carry resources or cost so the schedule reconciles with the estimate.

## Performance tests

- **Critical path test:** delay a critical activity artificially; the finish date should move by the same amount.
- **CPLI** and **BEI** — the critical path length index and the baseline execution index — both at least 0.95.

These numbers are not rules; they are thresholds that show where to look harder. A schedule that passes them can be relied on for control, and defended when a delay has to be analysed.
"""

BASELINE_DE = """\
Der Basisterminplan ist der Maßstab, an dem jeder spätere Fortschrittsbericht und jeder Verzugsanspruch gemessen wird. Ist seine Logik schwach, erbt alles, was darauf aufbaut, diese Schwäche. Die DCMA-14-Punkte-Prüfung ist eine verbreitete Checkliste dafür; das sind die wichtigsten Punkte.

## Logik

- **Fehlende Vorgänger oder Nachfolger:** außer Projektstart und -ende muss jeder Vorgang im Netz verknüpft sein. Grenzwert: 5 %.
- **Leads (negative Abstände):** keine. Sie verdecken eine Beziehung, die klar benannt werden sollte.
- **Lags:** höchstens 5 % der Beziehungen. Echte Wartezeit, etwa das Aushärten von Beton, wird besser als eigener Vorgang abgebildet.
- **Beziehungsarten:** mindestens 90 % Ende-Anfang (EA).

## Einschränkungen und Puffer

- **Harte Termine (Muss beginnen/enden am):** höchstens 5 %. Sie schneiden die Logik ab und erzeugen einen künstlichen kritischen Weg.
- **Hoher Puffer:** mehr als 44 Arbeitstage Gesamtpuffer deutet meist auf eine fehlende Verknüpfung; höchstens 5 %.
- **Negativer Puffer:** im Basisplan keiner.

## Dauern und Ressourcen

- **Lange Dauern:** höchstens 5 % der Vorgänge über 44 Arbeitstage — ein langer Vorgang lässt sich schlecht steuern.
- **Ungültige Termine:** ein Ist-Termin in der Zukunft oder eine Prognose in der Vergangenheit ist ein Fortschreibungsfehler.
- **Ressourcen:** Vorgänge sollten Ressourcen oder Kosten tragen, damit Terminplan und Kostenschätzung zusammenpassen.

## Leistungstests

- **Test des kritischen Wegs:** Verzögert man einen kritischen Vorgang künstlich, muss sich der Endtermin um denselben Betrag verschieben.
- **CPLI** und **BEI** — Critical Path Length Index und Baseline Execution Index — beide mindestens 0,95.

Diese Zahlen sind keine Gesetze, sondern Schwellen, die zeigen, wo genauer hinzusehen ist. Ein Terminplan, der sie besteht, trägt die Steuerung — und hält stand, wenn ein Verzug analysiert werden muss.
"""


ARTICLES = [
    {
        "slug": "choosing-a-delay-analysis-method",
        "published_at": dt.datetime(2026, 9, 15, 9, 0),
        "tags": ("delay-analysis", "project-control", "primavera"),
        "title_fa": "کدام روش تحلیل تأخیر؟ راهنمای انتخاب",
        "title_en": "Which delay analysis method? A guide to choosing",
        "title_de": "Welche Methode der Verzugsanalyse? Ein Leitfaden zur Auswahl",
        "abstract_fa": "پنج روش اصلی تحلیل تأخیر در پروژه‌های ساخت — از برنامه‌ی تأثیریافته تا برنامه‌ی اجراشده‌ی فروریخته — چه می‌سنجند، به چه سوابقی نیاز دارند و چه چیزی تعیین می‌کند کدام‌یک برای یک ادعای مشخص مناسب است.",
        "abstract_en": "The five main methods of construction delay analysis — from impacted as-planned to collapsed as-built — what each one measures, which records it needs, and what decides which one fits a given claim.",
        "abstract_de": "Die fünf wichtigsten Methoden der Verzugsanalyse im Bau — von Impacted As-Planned bis Collapsed As-Built: was jede misst, welche Unterlagen sie braucht und was darüber entscheidet, welche zu einem konkreten Anspruch passt.",
        "body_fa": DELAY_FA,
        "body_en": DELAY_EN,
        "body_de": DELAY_DE,
    },
    {
        "slug": "baseline-schedule-quality-checks",
        "published_at": dt.datetime(2026, 9, 22, 9, 0),
        "tags": ("planning", "primavera", "project-control"),
        "title_fa": "برنامه‌ی مبنای قابل‌اتکا: ۱۴ آزمون کیفیت",
        "title_en": "A baseline you can rely on: the 14 quality checks",
        "title_de": "Ein belastbarer Basisterminplan: die 14 Qualitätsprüfungen",
        "abstract_fa": "برنامه‌ی مبنا معیار سنجش همه‌ی پیشرفت‌ها و تأخیرهای بعدی است. مروری بر ارزیابی ۱۴ نقطه‌ای DCMA — منطق، قیدها، شناوری، مدت‌ها و آزمون مسیر بحرانی — و اینکه هر آستانه چه خطایی را آشکار می‌کند.",
        "abstract_en": "The baseline is what every later progress report and delay is measured against. A walk through the DCMA 14-point assessment — logic, constraints, float, durations and the critical path test — and the mistake each threshold exposes.",
        "abstract_de": "Der Basisplan ist der Maßstab für jeden späteren Fortschritt und jeden Verzug. Ein Gang durch die DCMA-14-Punkte-Prüfung — Logik, harte Termine, Puffer, Dauern und der Test des kritischen Wegs — und welchen Fehler jede Schwelle aufdeckt.",
        "body_fa": BASELINE_FA,
        "body_en": BASELINE_EN,
        "body_de": BASELINE_DE,
    },
]


class Command(BaseCommand):
    help = "Create the first two articles (fa/en/de) if they are missing."

    def add_arguments(self, parser):
        parser.add_argument("--update", action="store_true", help="Overwrite existing ones with this text.")

    @transaction.atomic
    def handle(self, *args, update=False, **options):
        tags = {}
        for slug, (fa, en, de) in TAGS.items():
            tags[slug], _ = Tag.objects.get_or_create(
                slug=slug, defaults={"name_fa": fa, "name_en": en, "name_de": de}
            )

        for row in ARTICLES:
            row = dict(row)
            slugs = row.pop("tags")
            row["published_at"] = timezone.make_aware(row["published_at"])
            slug = row.pop("slug")
            exists = Article.objects.filter(slug=slug).exists()
            if exists and not update:
                self.stdout.write(f"article: '{slug}' exists, left alone")
                continue
            article, _ = Article.objects.update_or_create(slug=slug, defaults=row)
            article.full_clean()
            article.tags.set([tags[s] for s in slugs])
            self.stdout.write(self.style.SUCCESS(f"article: '{slug}' {'updated' if exists else 'created'}"))
