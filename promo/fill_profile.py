# Run by promo/up.sh inside the promo container (manage.py shell). Fills only the
# EMPTY translated Profile columns from seed_profile, the same fix production got
# on 2026-10-15, so a backup taken before it still shows English and German.
from unittest import mock

from apps.content.management.commands.seed_profile import Command
from apps.content.models import Profile

real = Profile.load()
seed = Profile(pk=1)
with mock.patch.object(Profile, "load", return_value=seed), mock.patch.object(Profile, "save", lambda *a, **k: None):
    Command()._profile()

filled = []
for f in Profile._meta.concrete_fields:
    if f.name[-3:] in ("_fa", "_en", "_de") and not getattr(real, f.name) and getattr(seed, f.name):
        setattr(real, f.name, getattr(seed, f.name))
        filled.append(f.name)
real.save()
print("profile columns filled:", len(filled))
