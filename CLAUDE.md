# CLAUDE.md

Guidance for Claude Code (claude.ai/code) working in this repository.

## What this is

The personal site of **Hassan Naderirad** (حسن نادری‌راد) — a civil engineer
(MSc, construction management) working in project planning and control, delay
analysis and scheduling in Primavera P6 / MS Project. A portfolio, a blog and a digital
business card in one Django app, in **three languages** (Persian, English,
German). It is also the link and the QR code he hands people, so the two things
it must never be are slow and ugly.

The stance of the whole project: **a strong front end over a deliberately
small back end.** Nine views, one SQLite file, no API, no build step, no
JavaScript framework. Every design decision below exists to keep it that way
while still allowing the site to grow.

## Commands

**The site runs in Docker only** — not with a bare `runserver` on the host.
Every command goes through the container:

```bash
docker compose up --build -d                                     # port 8007
docker compose exec web python manage.py migrate                 # after any model change
docker compose exec web python manage.py makemigrations content
docker compose exec web python manage.py seed_profile            # the REAL content, idempotent
docker compose exec web python manage.py seed_profile --wipe     # replace projects/skills/roles
docker compose exec web python manage.py seed_articles          # the first two articles, fa/en/de — creates missing ones only
docker compose exec web python manage.py seed_demo               # placeholder content — overwrites the real profile
docker compose exec web python manage.py createsuperuser         # to reach /admin/
docker compose exec web python manage.py check
```

Tests live in `tests/` and run with `docker compose exec web python manage.py test tests`.
They are stock Django test classes so `pytest-django` can pick them up
unchanged later. `test_geo_language.py` pins the redirect; `test_pages.py` pins
every route in all three languages, the services offer, per-language post SEO,
the sitemap and the Markdown rendering.

## The shape of the project

```
config/        settings, urls, wsgi          — the whole Django configuration
apps/core/     views, forms, i18n strings, template tags, jalali
apps/content/  models, admin, seed command   — everything a visitor reads
templates/     base.html + one file per page
static/        site.css, app.js, self-hosted fonts
data/          db.sqlite3, media/, staticfiles/  — THE one volume in production
```

`data/` is the only directory that survives a redeploy, and everything
persistent is inside it on purpose: the database, uploads and collected static
are one mount, so hosting is one container and one disk.

## Content lives in the database, not in the code

**`seed_profile` is the real content and `seed_demo` will overwrite it.** Both
write `Profile.load()`, so running `seed_demo` on a live database replaces
Hassan's biography with placeholders. `seed_profile` is the reviewed record of
every public claim — it is the file to edit when a claim changes, not the admin
form, because the admin leaves no diff. Its docstring lists the claims that are
retired and must not come back, and the reasons education and every private
fact are absent.

`apps/content/models.py` holds every word a visitor reads. Nothing else in the
project contains copy — if you find yourself typing a sentence about Hassan into
a template, it belongs in a model field instead.

Twelve models: `Profile` (a singleton — `Profile.load()` is the only reader),
`Service`, `SkillGroup`/`Skill`, `Tag`, `Project`, `Experience`, `Post`/`PostImage`,
`Article`/`ArticleImage`, `Message`. `Post` and `Article` share the abstract
`Written` (languages, content language, lead image, reading time).

**Only claims Hassan has supplied are on the site.** No employer, project name,
figure or date is invented: the four `/projects/` entries are areas of practice
(delay analysis, baseline schedule, progress control, ICB project management),
and career/education rows, location, languages and contact channels stay empty
until he gives the real values — see `seed_profile`'s docstring.
**Project work is income, so it has its own page.** `Profile.offer_*` holds the
headline, lede and Markdown long form; `Service` rows are the promise cards
(end to end, quick start / fast delivery, agreed price, work modes). They show
as a peach band first on the home page and as `/services/`; "Start a project"
links to `/contact/?topic=project`, which pre-fills the subject. An empty
`offer_title` removes the page, the nav link, the band and the sitemap entry.

**Posts are written in the admin**, in whichever languages they exist in — no
language is required, `Post.clean()` asks for one complete title + body. The
body is Markdown rendered with `md_breaks` (a line break stays a line break, so
LinkedIn text pastes as-is; a bare `https://` becomes a link; off-site links open
in a new tab; images lazy-load). Images are uploaded as `PostImage` rows on the
post's own admin page, which shows the `![alt](url)` line to paste.
`original_url` renders a "originally posted on LinkedIn / X / …" link; the
platform comes from `Post.PLATFORMS`.

**Articles («مقالات», `/articles/`) are the long, citable pieces** — a journal
or conference paper, a technical write-up — where a post is a note. Written
in the admin the same way (any language, `Article.clean()` asks for a title
plus an abstract or body), with the publication fields a paper needs:
translated `venue`, `authors`, `doi`, `pdf`, `external_url`. A paper published
elsewhere can be just its abstract and PDF. It is lilac (writing), gets the
same per-language canonical/hreflang/sitemap treatment as a post
(`_language_seo` in `apps/content/views.py`), is a `ScholarlyArticle` in
JSON-LD when it has a venue or DOI, and — like the blog — its nav, footer and
palette entries appear only once one is published (`has_articles`).

Two deliberate absences:

- **`Skill` has no percentage.** A "90% Python" bar is a number nobody can
  verify and every reviewer discounts. `is_primary` is the only emphasis there
  is, and it means "show this in the hero strip".
- **There is no view counter and no "years of experience" field.** Both are
  claims a personal site cannot back up.

## Translation: one column per language

A translated field is **one real column per language**, named `<field>_<lang>`.
`@i18n_fields(...)` in `models.py` writes those columns so the model body stays
readable, and `Translatable.tr("title")` reads the active language with a
fallback chain that ends at Persian.

Why not `django-modeltranslation` or a per-language row: one dependency fewer,
every query stays a plain query with no join, the stock admin renders the three
inputs side by side for free, and **a fourth language is one entry in
`settings.LANGUAGES` plus one migration**. The cost is that an unfilled
language falls back rather than 404s, which is the behaviour a personal site
wants anyway.

In templates it is `{{ project|tr:"title" }}` and, for a Markdown field,
`{{ project|md:"body" }}`.

**UI strings are a different problem and have a different answer.** Buttons,
labels and section headings live in `apps/core/i18n.py` as one Python dict,
read with `{% t "nav.projects" %}`. Django's gettext catalogues need `.po`
files compiled by the `msgfmt` binary, which turns "reword a button" into a
build step that has to run on Windows, in CI and inside the image; this
vocabulary is about a hundred short strings. `LocaleMiddleware` is still what
activates the language — only the catalogue is ours.

**An unknown key renders as the key**, visibly, rather than as an empty string.

## URLs, and the language prefix

`i18n_patterns` with `prefix_default_language=False`: Persian is at `/`,
English at `/en/`, German at `/de/`. Everything a reader can see is inside that
block so a language switch is a real, shareable, indexable URL.

Machine endpoints stay **outside** it — `sitemap.xml`, `robots.txt`,
`feed.xml`, the `.vcf` and `/healthz`. There is nothing to translate about a
vCard, and a crawler should find one sitemap rather than three. That one
sitemap still lists every page in all three languages: `apps/core/sitemaps.py`
sets `i18n`, `alternates` and `x_default`, so each URL carries its hreflang
siblings — which is how the `/de/` pages get found by someone searching in
German.

**SEO lives in three places.** `base.html`'s head (title / description /
robots / canonical / hreflang / Open Graph blocks — `seo_title` and
`seo_description` on the profile are the home page's); the context processor
(`canonical_url` and `alternates`, both built from the path *without* its query
string); and `apps/core/seo.py`, which builds schema.org JSON-LD as dicts —
Person, WebSite, ProfilePage, BlogPosting, CreativeWork, Service, breadcrumbs —
emitted by `{% ld_* %}` from `seo_tags`. Never hand-write JSON-LD in a template.
A view can override with `seo_canonical`, `seo_alternates`, `seo_robots`. A
post opened in a language it is not written in keeps its fallback text but its
canonical names the language it has, its hreflang lists only real languages,
and the sitemap lists it only there (`get_languages_for_item`). The share image
is `Profile.og_image` → avatar, or a post's cover → first body image.

The header nav is in the order a reviewer reads a candidate — work, services,
résumé, about, writing — with contact as the one button in the bar. **The footer is the
site map**: every page grouped as explore / career / connect, plus the vCard,
RSS and `sitemap.xml`.

The switcher is built in `apps/core/context_processors.py` with Django's
`translate_url`, so it points at *this* page in the other language instead of
dumping the reader on the home page.

**A first visit picks its language by country.** `GeoLanguageMiddleware`
(`apps/core/middleware.py`) sends a first-time visitor on an unprefixed page
from Germany to `/de/…` and from any other *known* non-Iranian country to
`/en/…`; the mapping is `GEO_LANGUAGE_BY_COUNTRY` in settings. The country
comes from `apps/core/geo.py`: a proxy header (`DJANGO_GEO_COUNTRY_HEADER`)
first, then a MaxMind-format database at `data/geoip/country.mmdb`. The rules
that keep it from doing harm, all pinned in `tests/test_geo_language.py`:
it decides **once** (cookie `naderirad_geo`, set whether or not it redirected,
so the switcher's «فارسی» link sticks); it never redirects an explicit `/en/`
or `/de/` URL, a POST, a same-site Referer, or a **crawler** — redirecting
Googlebot (which crawls from the US) would de-index the Persian pages; and an
**unknown country changes nothing**, so a missing database never sends Iran to
English. `hreflang="x-default"` points at the unprefixed URL for this reason.

## The design system

**Colour lives in the three token blocks at the top of `static/css/site.css`
and nowhere else.** `:root` is the light theme; the two blocks after it restate
the same names for dark, once for `prefers-color-scheme` and once for an
explicit `[data-theme="dark"]`, so an explicit choice beats the device in both
directions. A rule that needs a tint writes `rgba(var(--mint-rgb), .12)`, never
a second hex. Re-theming the site is editing values in those blocks. The two
`--bg` values are also written in `base.html`'s `theme-color` meta tags and in
`THEME_COLOR` in `app.js`.

The palette is **four pastels, each with one meaning**:

| hue | means | where |
|---|---|---|
| mint (`--mint`) | the work, and anything actionable | projects, nav, primary buttons |
| sky (`--sky`) | the career | timeline, résumé, facts |
| peach (`--peach`) | the person | availability, «این روزها», contact |
| lilac (`--lilac`) | writing, and nothing else | posts, so a post tag never reads as a project |

A fifth hue would need a fifth meaning, which is the reason not to add one.

**Each hue is a five-step ramp, not one value**: `--x-tint`, `--x-soft`,
`--x`, `--x-strong`, `--x-deep`, plus `--x-rgb` for tints. A card, its border,
its icon and its label can be one colour at four intensities. What each step
is *for* is the rule to keep:

- `-tint` is a ground you can barely see, `-soft` is a fill, `--x` is the
  pastel itself (a button, a dot, a hover border).
- **Only `-strong` and `-deep` may colour a letterform**: `-strong` on
  `--surface` or `-tint` (≥ 4.5:1), and **on a `-soft` fill only `-deep`**
  (mint and peach `-strong` fall to 4.3–4.5:1 there).
- Text **on the pastel `--x` itself is `--on-accent`**, which is ink. That is
  why a primary button is a pastel with dark lettering rather than a saturated
  fill with white: it keeps the page pastel and still AA (8:1 or better).

In dark the ramp inverts — `-deep` is the *lightest* step — so a rule that
asked for `-deep` because it was drawing text keeps getting the readable step
without knowing about the theme.

**`--accent-*` is an indirection, not a fifth colour.** An element carrying
`data-accent="peach"` (or `"sky"`, `"lilac"`, `"mint"`) re-points the whole
ramp for itself and everything inside it, so every eyebrow, pill, chip, tag,
button and link in that subtree follows. Re-colouring a section is one
attribute in the template and no new CSS. Prefer `var(--accent-…)` over
`var(--mint-…)` in any component that could appear in more than one context.

**Where a hue *carries* something it means something; where it is only a
field it is rhythm.** Tags, links, buttons and post rows are the first kind and
keep the meanings above. Rows of near-identical boxes — case covers, project
cards, skill groups, fact tiles, contact channels, footer columns, the tech
ribbon — are the second: their container carries **`.rhythm`**, whose children
take turns through all four hues, so four boxes read as four boxes. Removing
the class is how a row goes back to one hue.

**A section can be a band.** `.sec.sec-band` paints the section edge to edge in
its own accent's `--wash-*` with a hairline dot texture. Bands alternate with
plain sections down the home page (work → *career band* → toolbox → *writing
band* → contact), which is what gives a long page a horizontal rhythm.

**A page can carry a photo wash.** `.photo-wash` paints a portrait in the
section's accent — photo over `--accent` with `background-blend-mode:
luminosity` — so any photo matches the palette in both themes; strength is
`--photo` / `--photo-fx`, set per theme (`Profile.backdrop_services` /
`backdrop_resume`; empty draws nothing). On `/services/` it is `.photo-stand`:
the whole figure, `position: fixed` at the inline end so it stays in view the
length of the page, every edge feathered by two intersected masks, with
its own `--photo-stand` strength (fainter in light) and a `.photo-lit` twin
that `initPointer()` aims at the pointer, since the photo lies under the
content and cannot be hovered. In the
résumé card it is two copies spanning the card: a barely-there one, and
`.photo-lit`, masked to a circle at data-spot's `--mx/--my`, which comes up on
hover like a flashlight on the face (fine pointer, motion allowed). It sits
over the ambient field, never replaces it, and is hidden in print.

**Nothing may bleed sideways.** The hero aurora is an element with
`overflow: hidden`, and `.page-head::before` bleeds *up* behind the
transparent header but has `inset-inline: 0`. A negative inline inset or a
`left: -9999px` is scrollable overflow in RTL: the Persian page opens shifted
by exactly that much, while English looks fine. `html` carries
`overflow-x: clip` as the last line of defence, and **`<body>` must not carry
any `overflow-x`** — next to `clip` on `html` it turns `<body>` into its own
scroll container and the sticky header stops sticking.

**`[hidden]` always wins** (`display: none !important` in the base). Without
it a component's own `display: grid` beats the attribute, and a closed
popover, a filtered-out card and the pre-JS back-to-top button all show.

**Motion has one vocabulary.** Two easings, `--ease` (settle) and `--spring`
(a small overshoot, for things that pop); hover lifts use `transform`, arrivals
use the individual `translate`/`scale` properties, so the two never overwrite
each other. **The whole site sits on `.ambient`** (first child of `<body>`): a
fixed, self-clipped layer of four pastel lights drifting on 22–32 s cycles,
turned by scroll through a scroll-driven `rotate` (no JS), plus grain and a
faint blueprint grid (`.ambient::before`); over them `initAmbient()` draws a
schedule network (activity boxes and milestone diamonds linked finish-to-start,
progress travelling the links, Gantt bars slipping behind their baselines,
rising planning terms) in the `--x-rgb` colours. **On top of that,
`initBuild()` puts up a building as the page is read**: the scroll *is* the
project's progress — surveyed plot at the top, then piles, the frame storey by
storey with a tower crane climbing beside it, the façade trailing a few
storeys, topping out, the crane coming down and the lights coming on at
handover at the foot of the page. It is a pure function of one `progress`
number that eases toward the scroll and stops when it arrives (nothing runs
while the page is still); scrolling up takes it down again. It stands at the
inline end (drawn LTR, mirrored for RTL, labels unmirrored), and under reduced
motion the finished building is drawn once. Bands are 62 % opaque
(`color-mix`) so it stays in view through them. Strength is the
`--ambient`, `--net` and `--build` tokens, set per theme. Every decorative loop —
the ambient field, the aurora drift, the portrait halo, the
floating skill chips, the tech ribbon — sits behind
`prefers-reduced-motion`, which also stops the ribbon and wraps it.

**Logical properties only.** The site runs RTL in Persian and LTR in English
and German from the same rules: `padding-inline-start`, never `padding-left`.
A rule with a physical side in it is a bug in one of the three languages.

**Three typefaces, all self-hosted.** Vazirmatn for everything Persian and all
UI, Fraunces for Latin display (the name, the card index, the error code) and
IBM Plex Mono for labels, dates and technology names. Nothing this page draws
with comes off a CDN — inside Iran `fonts.googleapis.com` is slow at best.
Latin runs inside Persian text carry `.lat` or `.mono`, which set
`direction: ltr; unicode-bidi: isolate`, or a Latin word flips inside a Persian
sentence.

**The theme has three states**, not two: `system` / `light` / `dark`, stored
under `localStorage["naderirad-theme"]`. That key is read **twice**: by
`app.js`, and by a small blocking script in `base.html`'s `<head>`. The second
one is pre-paint on purpose — deferring it to `app.js` repaints one frame in,
which is exactly the flash it prevents. **If you rename the key, rename it in
both places.**

## JavaScript is enhancement, and only enhancement

`static/js/app.js` is one file, no dependency, no build. Turn JavaScript off
and every link, form and page still works; what is lost is polish.

Fourteen concerns, each its own function started from `boot()`: theme; the
ambient network; the scroll-built building; header
(frosting, reading progress, back-to-top, mobile nav); nav indicator;
popovers; tooltips; reveal-on-scroll; pointer effects; tag filter;
copy-to-clipboard; share; the contact form's counter and sending state;
command palette.

**The search button carries no "Ctrl K" hint**, on purpose: in Chrome that
chord belongs to the address bar and searches Google, so a hint under the icon
promised something the page cannot deliver. The palette still opens on `/`.

The rules worth keeping:

- **Reveal-on-scroll's resting state is visible.** The hidden state exists only
  while `.js` is on the root element and motion is allowed. No observer, or
  `prefers-reduced-motion`, and everything is simply shown — content parked at
  `opacity: 0` waiting for a callback that never fires is the classic way this
  feature fails silently. The arrival is a CSS *animation* staggered by `--d`,
  not a transition with an inline `transition-delay`: that delay would also
  delay every hover on the card for the rest of the visit.
- **Tooltips are `data-tip="…"`, and they decorate a name the element already
  has.** One floating element, placed in viewport pixels, flipped below when
  there is no room above, clamped to both edges; mouse hover and keyboard focus
  only. An icon button still needs its `aria-label` — on touch that label is
  all there is.
- **Pointer effects are fine-pointer only and off under reduced motion.**
  `data-spot` is the soft light that follows the pointer inside a card (it uses
  the card's `::after`, so a spotlit component must not need its own);
  `data-tilt="n"` tilts by up to n degrees (the portrait, the business card).
- **The tag filter is client-side because the whole list is already on the
  page.** The query string is kept in step so a filtered view is still
  shareable, and the chip for `?tag=` is pressed on a cold load. If the list
  ever outgrows one render, this becomes a server-side filter and the chips
  become links. The count on each chip comes from `_tags_for()` in
  `apps/content/views.py`.

The command palette (Ctrl/⌘+K, or `/`) reads its index (`cmdk_index`) from the
context processor, shipped inside the page as JSON, so opening it costs no
request and it can never disagree with what the site actually has. Each entry
carries `i`, an icon id from `templates/partials/icons.html`. The language and
theme shortcuts are read from the header itself. It costs two small queries per
request; if the site grows past a few hundred rows, cache the list — do not
make the palette fetch.

## Dates: Jalali for Persian, Gregorian for the rest

Storage stays Gregorian and UTC. **Every date a Persian reader sees is rendered
Jalali by the server**, through `apps/core/jalali.py` (pure arithmetic, no
dependency) and the `smart_date` filter — so the first paint is already correct
and nothing has to be repaired by JavaScript a frame later. English and German
readers get the Gregorian date and their own month names. Persian digits come
from `fa_num`, which is a no-op in the other two languages.

How long a role ran is the `{% duration start end %}` tag: whole months counted
inclusively, the way a CV counts them — "2 yrs 5 mos", "2 J. 5 Mon.",
"۲ سال و ۵ ماه". It is arithmetic on the two dates printed beside it, not a
stored claim, so there is still no years-of-experience field anywhere.

## The contact form

`POST` → save → `redirect` with `?sent=1`, so a refresh can never resend.
Protection is a **honeypot** (`website`, invisible inside the form's own box
via `.hp` — never `left: -9999px`, which scrolls the Persian page sideways) plus a
per-session 60-second throttle from `settings.CONTACT_RATE_LIMIT_SECONDS`. No
captcha: for the volume a personal site attracts, a field a human never sees is
enough, and it costs the reader nothing.

**Email and phone are each optional, one is required.** They are one
`fieldset.reach` with one hint and one error, because the rule is about the
pair. `ContactForm.clean()` raises it (code `reach`, only when neither field
already has its own error), app.js repeats it before sending, and the
`message_has_reply_channel` CheckConstraint is the database's backstop. A phone
is stored normalised by `normalize_phone` (Persian digits → ASCII, separators
dropped, `00` → `+`, 7–15 digits). Pinned in `tests/test_contact.py`.

A spam submission is answered **with the same redirect a real one gets**. A bot
that can tell the difference will tune around the trap.

**Every saved message goes to the Bale bot** (`apps/core/bale.py`, stdlib
only): posted to each chat in `BALE_CHAT_IDS` with five buttons —
`Message.Status` new / read / rejected / archived / starred — and a press
changes the status and redraws the notification. Only chats in
`BALE_CHAT_IDS` may press or use `/new` and `/starred`; anyone else who writes
to the bot gets only their chat id (that is how the owner finds theirs). Sending
runs in a daemon thread so a slow Bale never delays the redirect. Updates come
to `/bale/<secret>/` (outside the language prefix; the secret is derived from
`SECRET_KEY`), registered on boot by `start.sh` → `bale_webhook`, which needs
an https `DJANGO_SITE_URL`; without one, `manage.py bale_poll` long-polls
instead. No token → nothing is sent. Pinned in `tests/test_bale.py`.

Nothing is emailed. Messages land in the database and are read at
`/admin/content/message/`. Adding email means one `send_mail` in
`apps.core.views.contact` and SMTP settings — deliberately not done, because an
SMTP credential in a container is a real cost and the admin list already works.

## The digital business card

`/card/` is one screen made to be handed over, and `/card/naderirad.vcf` is a
real vCard so a phone saves the contact rather than a screenshot. The QR is
rendered **server-side** by `segno` as inline SVG: it prints, it survives a
screenshot, and it needs no JavaScript to exist.

`segno` will not accept `currentColor`, so the code is drawn in a sentinel hex
and swapped in `apps/core/views.py`. That is what lets one SVG be legible in
both themes without rendering the QR twice.

## The admin, and the panel that is coming

`django.contrib.admin` is registered and is the **interim** way to edit
content. The lightweight custom panel is a later piece of work; when it is
built it belongs in `apps/panel/` as its own app with its own templates,
reusing `site.css`'s tokens, and the stock admin can then be switched off in
one line. Until then, do not build admin-shaped branches into the public pages
— the two audiences are different and the panel is a screen of its own.

**Every file field in the admin uses `UploadWidget`** (`formfield_overrides =
UPLOADS` in `apps/content/admin.py`, plus `static/content/upload.js` and
`upload.css`). The stock input shows only a file name, and a chosen file is sent
only when the form is saved, so on the long profile form the photo looked
applied when it was not. The widget shows the file that is live now, a preview
of the one waiting, an «منصرف شدم» undo, and a fixed bar with «ذخیره» (it
submits as "save and continue") until the form is sent; leaving with a file
waiting asks first. `ProfileAdmin` puts the photos first, has save buttons at
the top too, and its list redirects to the one profile, so «ذخیره» comes back
to the form with the success message. Pinned in `tests/test_admin_upload.py`.

## Production: where and how this site is live

> A deploy changes the **live** site. Ask the user before deploying.

| | |
|---|---|
| URL | https://hasan-naderi.ir (`www.` and `http://` redirect here) |
| Server | VPS `91.207.18.218` (Webdade, Ubuntu 24.04). From Windows: `ssh vps` → user `deploy` (key login, passwordless sudo, in the `docker` group) |
| App dir | `/srv/hesam-ir/`: code (replaced on every deploy), `.env` (production secrets, only on the server), `data/` (the volume; deploy never touches it) |
| Container | published on `127.0.0.1:8007` → 8000. Only Caddy is public (ports 80/443) |
| Reverse proxy | Caddy on the host, automatic Let's Encrypt HTTPS. Config source `G:\Repos\devops\server\caddy\Caddyfile`, applied with `bash /g/Repos/devops/caddy-apply.sh` |
| Runbook | `G:\Repos\devops\RUNBOOK.md` (server layout, logs, restart, backups, DNS). Keep it updated after any server change |
| Source code | GitHub `MehDiSDeveloper/hesam-ir` (public). Only a backup/history: deploy uploads the local working copy, not git |

**Deploy** (Windows PowerShell; takes the **local working copy**, uncommitted changes included, git is not involved):

```
G:\Repos\devops\deploy.ps1 hesam-ir
```

It uploads the repo without `.git`, `.venv`, `node_modules`, `.next`, `.env*`, `data/` and the dev-only compose file,
strips CRLF from `*.sh`, rsyncs into `/srv/hesam-ir/` (keeping `.env` and `data/`), runs `docker compose up -d --build`
and waits for a 200 on `http://127.0.0.1:8007/healthz`. Migrations run in the container's start script, so there is no manual step.

**Compose on the server.** The server `.env` sets `COMPOSE_FILE=docker-compose.yml:docker-compose.prod.yml`, so a plain `docker compose …` in `/srv/hesam-ir` uses the prod override. `docker-compose.prod.yml` is not in this repo; it lives in `G:\Repos\devops\server\hesam-ir\` and is shipped by `deploy.sh`. It replaces the port with `127.0.0.1:8007`. `docker-compose.override.yml` is dev-only and is never uploaded.
If you change the service name, the container port or the published port here, update `G:\Repos\devops\`
(`deploy.sh`, `server/hesam-ir/`, the Caddyfile) in the same change, or the live site breaks.

**Production environment** lives only in `/srv/hesam-ir/.env` (mode 600). A new variable the code needs must be added there too,
not only to `.env.example`. Change a key without opening the file (it backs up `.env` and re-creates the container):
`printf 'KEY=value\n' | bash /g/Repos/devops/env-set.sh hesam-ir`. Never print, copy into chat or commit its values.

**Look at the live app:**

```
ssh vps "cd /srv/hesam-ir && docker compose ps && docker compose logs --tail 100"
```

**Backups:** `data/` is backed up every night (03:30) to `/var/backups/apps/` on the server and pulled daily to `G:\apps backup` on Windows; 14 days are kept in each place. How to restore: RUNBOOK → Backups.

**Specific to this app:**

- Uploads (`/media/`) are served by **Caddy** from `/srv/hesam-ir/data/media`, because Django serves them only with `DEBUG` on.
- The admin login comes from `DJANGO_ADMIN_USERNAME` / `DJANGO_ADMIN_PASSWORD` in the server `.env` (`ensure_admin` on every boot).
  Without them it would create the default `hesam` / `raad505`, so never remove them.
- The Bale bot token in the server `.env` is the **production** bot. `start.sh` registers the webhook
  `https://hasan-naderi.ir/bale/<secret>/` on every boot. Don't run the same token locally: use a separate test bot in the local `.env`.
- `start.sh` is saved with CRLF on Windows. `deploy.sh` fixes that on upload; the image itself would not start with CRLF.
- The live database started empty on 2026-09-30 with `seed_profile` + `seed_articles`. **Never run `seed_demo` on the server**:
  it overwrites the real profile.
- One-off commands: `ssh vps "cd /srv/hesam-ir && docker compose exec -T web python manage.py <cmd>"`.

## Deployment

One container, one process, one volume:

```
docker compose up --build     # or: docker build -t naderirad . && docker run …
```

`start.sh` is the whole boot: `migrate`, then `ensure_admin`, then
`collectstatic`, then gunicorn. **`ensure_admin` guarantees the owner's login**:
it creates the superuser `hesam` / `raad505` (or `DJANGO_ADMIN_USERNAME` /
`DJANGO_ADMIN_PASSWORD`) if it is missing, and re-enables active/staff/superuser
on it if it exists; a password changed in the admin is kept unless
`--reset-password` is passed. The dev override's command runs it too.
WhiteNoise serves static with a one-year cache and a hashed manifest outside
`DEBUG`. Uploads under `data/media/` are served by Django in `DEBUG` and by the
front proxy or WhiteNoise in production — **if uploads 404 on the host, that is
the thing to check first.**

Environment variables are documented in `.env.example`. Only two matter:
`DJANGO_SECRET_KEY` (rotating it logs out every admin session) and
`DJANGO_ALLOWED_HOSTS`. Set `DJANGO_SITE_URL` to the real domain — the canonical
tag, the `hreflang` alternates, the sitemap and **the QR code** all read it, so
a wrong value ships a QR pointing at the wrong host.

## Where this grows, and how

Each of these is a small, contained change. None needs the design above
rewritten:

- **A fourth language.** One entry in `settings.LANGUAGES`, one migration, one
  column in `apps/core/i18n.py`'s dict, one entry in `templatetags`' month names.
- **The lightweight admin panel.** `apps/panel/`, see above.
- **Email on a new message.** One `send_mail` call in `contact`.
- **Photos on projects.** The field is already there (`Project.cover`); the
  card and the detail page already render it when present.
- **A `/now` page.** `Profile.now_*` already holds the sentence; a page would
  be a longer version of the same field.
- **Postgres.** One dict in `settings.DATABASES` and `psycopg` in
  `requirements.txt`. Nothing in the app knows which backend it is on. Do this
  when concurrent writes get heavy or a second machine needs the same data —
  not before, because a separate database is the single biggest line on the
  hosting bill.
- **Tests.** The three worth writing first: every route answers 200 in all
  three languages; `Translatable.tr` falls back rather than returning empty;
  and the contact form's honeypot and throttle both refuse without saving.

## Things that will bite

- **`{# … #}` in a Django template is single-line only.** A multi-line one
  leaks into the rendered page as visible text. Use `{% comment %}` for
  anything over one line — every long comment in `templates/` already does.
- **Every views module that renders a translated field must load `site_tags`.**
  `{% load site_tags %}` at the top; forgetting it is a render-time error, not
  a silent miss.
- **`Profile.save()` forces `pk = 1`.** There is one person on a personal site.
  Do not try to create a second row.
- **`data/` is in `.gitignore` and `.dockerignore`.** The database is never
  committed and never baked into the image.
- **Every key in `Profile.links` needs two things**: an icon `#i-<key>` in
  `templates/partials/icons.html` and a label `channel.<key>` in
  `apps/core/i18n.py`. The key for mail is `email`, not `mail` — both icon ids
  exist for that reason. A missing icon is an empty button; a missing label
  renders as the key.
- **The QR plate is light in both themes** (`--qr-plate`, `--qr-ink`, defined
  once in `:root`). Do not "fix" it to follow dark mode: many phone cameras
  cannot read a light-on-dark code.
- **Fixed background layers are sized in `lvh`/`svh`, never `dvh` or
  `innerHeight`.** On a phone the address bar slides away at the start of a
  scroll and the dynamic viewport grows. Anything sized to it resizes and
  jumps, and a canvas whose size changes is also cleared. The canvases measure
  their own box and skip a resize that changes nothing. The network also keeps
  running through a touch scroll, because pausing it froze the background
  under the finger.
- **In the preview pane, a hidden or covered window pauses animation frames,
  CSS animations and `IntersectionObserver`.** Screenshots of a scrolled page
  then come back blank and the header never reports `is-stuck`. That is the
  pane, not the page — check with computed styles, or inject a style that
  zeroes animation and add `.is-in` to every `.reveal` before capturing.
