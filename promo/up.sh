#!/usr/bin/env bash
# Start the promo copy of the site on http://127.0.0.1:8017 with the REAL
# content: the newest nightly backup of production's data/ (pulled to
# "G:\apps backup" every day), unpacked into data/promo/. Production and the
# dev database are never touched. Contact messages are deleted from the copy
# because they are visitors' private data and must not appear in a video.
#   bash promo/up.sh            # restore the newest backup (only if data/promo is empty)
#   bash promo/up.sh --fresh    # throw data/promo away and restore again
set -euo pipefail
cd "$(dirname "$0")"
BACKUPS="${BACKUPS:-/g/apps backup}"

DATA=../data/promo
if [ "${1:-}" = "--fresh" ]; then rm -rf "$DATA"; fi
if [ ! -f "$DATA/db.sqlite3" ]; then
  latest="$(ls -d "$BACKUPS"/20*/ | sort | tail -1)"
  echo "restoring $latest/hesam-ir.tar.gz"
  mkdir -p "$DATA"
  tar -xzf "$latest/hesam-ir.tar.gz" --strip-components=1 -C "$DATA"
fi

docker compose up --build -d
for _ in $(seq 60); do
  curl -sf --noproxy '*' --max-time 3 http://127.0.0.1:8017/healthz >/dev/null && break
  sleep 1
done
docker compose exec -T web python manage.py shell -c \
  "from apps.content.models import Message; print('messages removed:', Message.objects.all().delete()[0])"
echo "promo site: http://127.0.0.1:8017"
