#!/usr/bin/env bash
# Usage: ./make_carousel.sh slides.json   -> out/carousel/slide-01.png ... slide-07.png
set -euo pipefail
cd "$(dirname "$0")"
JSON=$(realpath "${1:?usage: make_carousel.sh slides.json}")
rm -rf out/carousel && mkdir -p out/carousel
python3 render.py "$JSON" out/carousel
ls out/carousel
