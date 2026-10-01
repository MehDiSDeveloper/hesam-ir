"""The profile's photos can be changed, undone and removed from the admin.

A chosen file only travels when the form is saved; these pin that the save
lands the file, that the page it returns to shows it, and that "clear" empties it.
"""

import shutil
import tempfile
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image

from apps.content.models import Profile

MEDIA = tempfile.mkdtemp()


def png(name="me.png"):
    buf = BytesIO()
    Image.new("RGB", (4, 4), "teal").save(buf, "PNG")
    return SimpleUploadedFile(name, buf.getvalue(), content_type="image/png")


@override_settings(MEDIA_ROOT=MEDIA, GEO_LANGUAGE_ENABLED=False)
class ProfilePhotoTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def setUp(self):
        user = get_user_model().objects.create_superuser("owner", "o@example.com", "pw")
        self.client.force_login(user)
        p = Profile.load()
        p.full_name_fa, p.headline_fa, p.intro_fa = "حسن", "برنامه‌ریزی", "معرفی"
        p.save()
        self.url = f"/admin/content/profile/{p.pk}/change/"

    def form(self, **extra):
        return {"full_name_fa": "حسن", "headline_fa": "برنامه‌ریزی", "intro_fa": "معرفی", "is_available": "on", **extra}

    def test_the_list_opens_the_form(self):
        self.assertRedirects(self.client.get("/admin/content/profile/"), self.url)

    def test_the_form_starts_with_the_photos_and_explains_itself(self):
        page = self.client.get(self.url).content.decode()
        self.assertIn("content/upload.js", page)
        self.assertIn("data-upload", page)
        self.assertLess(page.index('name="avatar"'), page.index('name="full_name_fa"'))

    def test_save_puts_the_photo_on_the_site_and_shows_it(self):
        response = self.client.post(self.url, self.form(avatar=png()), follow=True)
        avatar = Profile.load().avatar
        self.assertTrue(avatar.name.startswith("profile/me"))
        self.assertContains(response, 'class="upload-live"')
        self.assertContains(response, avatar.url)
        self.assertContains(self.client.get("/"), avatar.url)

    def test_clear_removes_it(self):
        self.client.post(self.url, self.form(avatar=png()))
        self.client.post(self.url, self.form(**{"avatar-clear": "on"}))
        self.assertFalse(Profile.load().avatar)
