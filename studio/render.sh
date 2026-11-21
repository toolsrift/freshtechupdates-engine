#!/usr/bin/env bash
# Render a storyboard built by tools/build.py.
#   ./render.sh out/props.json out/video.mp4          full video
#   ./render.sh out/props.json out/still.png 120      one frame (for checks)
set -euo pipefail
cd "$(dirname "$0")"
PROPS=$(realpath "${1:?props.json}"); OUT=${2:?output}; FRAME=${3:-}
BROWSER=${CHROME_PATH:-/usr/bin/google-chrome}
COMMON=(--props="$PROPS" --browser-executable="$BROWSER" --gl=angle --log=error)
if [ -n "$FRAME" ]; then
  npx remotion still src/index.ts Video "$OUT" --frame="$FRAME" "${COMMON[@]}"
else
  npx remotion render src/index.ts Video "$OUT" --concurrency=2 --crf=20 "${COMMON[@]}"
  ffprobe -v error -show_entries format=duration:stream=codec_type,width,height -of compact "$OUT"
fi
