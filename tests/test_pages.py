"""Every page answers, the services offer works, and posts tell search engines the truth.

These need a database, so they are TestCase rather than SimpleTestCase — still
the stock Django class, which pytest-django runs unchanged.
"""

import os
from io import StringIO
from unittest import mock

from django.test import TestCase, override_settings

from django.contrib.auth import get_user_model
from django.core.management import CommandError, call_command

from apps.content.models import Article, Post, Profile, Service
from apps.core.templatetags.site_tags import md_breaks_field


@override_settings(GEO_LANGUAGE_ENABLED=False, SITE_URL="https://hesam.ir")
class PageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        p = Profile.load()
        p.full_name_fa, p.full_name_en = "حسن نادری‌راد", "Hassan Naderirad"
        p.headline_fa, p.intro_fa = "برنامه‌ریزی و کنترل پروژه", "معرفی"
        p.offer_title_fa, p.offer_title_en = "پروژه از صفر تا صد", "Projects end to end"
        p.offer_lede_fa = "توضیح"
        p.save()
        Service.objects.create(title_fa="از صفر تا صد", body_fa="همه‌ی مسیر", icon="layers")
        cls.fa_post = Post.objects.create(slug="both", title_fa="نوشته", body_fa="متن", title_en="Post", body_en="Text")
        cls.en_post = Post.objects.create(
            slug="english-only",
            title_en="English only",
            body_en="See https://example.com/x.",
            original_url="https://www.linkedin.com/posts/abc",
        )
        cls.paper = Article.objects.create(
            slug="paper",
            title_fa="مقاله",
            abstract_fa="چکیده",
            title_en="Paper",
            abstract_en="Abstract",
            venue_en="Journal of Construction",
            doi="10.1000/xyz",
        )
        Article.objects.create(slug="essay-en", title_en="Essay", body_en="Long **text**.")

    def test_every_page_answers_in_every_language(self):
        pages = ["", "about/", "services/", "contact/", "card/", "resume/", "projects/", "blog/", "blog/both/", "blog/english-only/", "articles/", "articles/paper/", "articles/essay-en/"]
        for prefix in ("/", "/en/", "/de/"):
            for page in pages:
                with self.subTest(url=prefix + page):
                    self.assertEqual(self.client.get(prefix + page).status_code, 200)

    def test_services_disappear_without_an_offer(self):
        Profile.objects.update(offer_title_fa="", offer_title_en="")
        self.assertEqual(self.client.get("/services/").status_code, 404)
        self.assertNotContains(self.client.get("/"), 'href="/services/"')

    def test_start_a_project_fills_the_subject(self):
        self.assertContains(self.client.get("/en/contact/?topic=project"), 'value="Project enquiry"')

    def test_hreflang_and_canonical_ignore_the_query_string(self):
        html = self.client.get("/en/projects/?tag=python").content.decode()
        self.assertIn('<link rel="canonical" href="https://hesam.ir/en/projects/">', html)
        self.assertIn('hreflang="x-default" href="https://hesam.ir/projects/"', html)
        self.assertNotIn("?tag=python\"", html.split("</head>")[0])

    def test_untranslated_post_points_canonical_at_its_real_language(self):
        html = self.client.get("/blog/english-only/").content.decode()
        self.assertIn('<link rel="canonical" href="https://hesam.ir/en/blog/english-only/">', html)
        # The language switcher in the body still links to /blog/…; only the head's alternates must not.
        self.assertNotIn('<link rel="alternate" hreflang="fa"', html)
        self.assertIn('<link rel="alternate" hreflang="en"', html)
        self.assertIn('lang="en" dir="ltr"', html)

    def test_post_links_to_its_original(self):
        response = self.client.get("/en/blog/english-only/")
        self.assertContains(response, 'href="https://www.linkedin.com/posts/abc"')
        self.assertContains(response, "Originally posted on LinkedIn")
        self.assertContains(response, '"@type":"BlogPosting"')

    def test_sitemap_lists_a_post_only_in_its_languages(self):
        xml = self.client.get("/sitemap.xml").content.decode()
        # The host is the request's (testserver here); the paths are the point.
        self.assertEqual(xml.count("blog/english-only/</loc>"), 1)
        self.assertIn("/en/blog/english-only/</loc>", xml)
        self.assertIn("/services/</loc>", xml)

    def test_post_needs_one_complete_language(self):
        from django.core.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            Post(slug="empty").clean()
        with self.assertRaises(ValidationError):
            Post(slug="half", title_de="Titel").clean()


    def test_article_page_shows_its_publication(self):
        html = self.client.get("/en/articles/paper/").content.decode()
        self.assertIn("Journal of Construction", html)
        self.assertIn('href="https://doi.org/10.1000/xyz"', html)
        self.assertIn('"ScholarlyArticle"', html)
        self.assertContains(self.client.get("/"), 'href="/articles/"')

    def test_untranslated_article_points_canonical_at_its_real_language(self):
        html = self.client.get("/articles/essay-en/").content.decode()
        self.assertIn('<link rel="canonical" href="https://hesam.ir/en/articles/essay-en/">', html)

    def test_articles_disappear_when_none_is_published(self):
        Article.objects.update(is_published=False)
        self.assertNotContains(self.client.get("/"), 'href="/articles/"')
        self.assertEqual(self.client.get("/articles/paper/").status_code, 404)

    def test_article_needs_a_title_and_an_abstract_or_body(self):
        from django.core.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            Article(slug="x").full_clean()
        with self.assertRaises(ValidationError):
            Article(slug="x", title_en="Only a title").full_clean()
        Article(slug="x", title_en="t", abstract_en="a", doi="https://doi.org/10.1/a").full_clean()


@mock.patch.dict(os.environ, {"DJANGO_ADMIN_USERNAME": "hesam", "DJANGO_ADMIN_PASSWORD": "from-the-env"})
class EnsureAdminTests(TestCase):
    def test_creates_the_admin_once_and_keeps_the_env_login_working(self):
        call_command("ensure_admin", stdout=StringIO())
        user = get_user_model().objects.get(username="hesam")
        self.assertTrue(user.is_superuser and user.is_staff and user.check_password("from-the-env"))
        self.assertTrue(self.client.login(username="hesam", password="from-the-env"))

        user.is_active = user.is_staff = False
        user.set_password("changed")
        user.save()
        call_command("ensure_admin", stdout=StringIO())
        user.refresh_from_db()
        self.assertTrue(user.is_active and user.is_staff)
        self.assertTrue(user.check_password("from-the-env"))  # the .env wins on every boot
        self.assertEqual(get_user_model().objects.count(), 1)

    def test_refuses_to_run_without_a_password(self):
        with mock.patch.dict(os.environ, {"DJANGO_ADMIN_PASSWORD": ""}):
            with self.assertRaises(CommandError):
                call_command("ensure_admin", stdout=StringIO())
        self.assertFalse(get_user_model().objects.exists())


class MarkdownTests(TestCase):
    def test_bare_links_line_breaks_and_images(self):
        post = Post(title_en="t", body_en="line one\nline two https://example.com/a.\n\n![pic](/media/p.png)")
        html = str(md_breaks_field(post, "body"))
        self.assertIn("<br", html)
        self.assertIn('<a href="https://example.com/a" rel="noopener" target="_blank">https://example.com/a</a>.', html)
        self.assertIn('loading="lazy"', html)
