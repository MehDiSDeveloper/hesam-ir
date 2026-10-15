#!/usr/bin/env bash
# Remove the promo copy completely: container, its image and data/promo/.
# The recordings in G:\Repos\promo\hesam-ir\ are kept.
set -euo pipefail
cd "$(dirname "$0")"
docker compose down --rmi local --volumes --remove-orphans
rm -rf ../data/promo
echo "promo copy removed"
