#!/usr/bin/env bash
# Usage: ./make_reel.sh reel.json [comic|paper|blueprint|neon]  -> out/freshtechupdates-reel.mp4
# With no style given, the style rotates by weekday (India time):
#   Mon/Wed/Fri/Sun = comic, Tue/Thu = paper, Sat = blueprint
set -euo pipefail
cd "$(dirname "$0")"
JSON=$(realpath "${1:?usage: make_reel.sh reel.json [style]}")
STYLE=${2:-}
if [ -z "$STYLE" ]; then
  case $(TZ=Asia/Kolkata date +%u) in
    1|3|5|7) STYLE=comic ;;
    2|4) STYLE=paper ;;
    6) STYLE=blueprint ;;
  esac
fi
rm -rf reelproj && mkdir -p out
if [ "$STYLE" = "neon" ]; then
  python3 hfreel.py "$JSON" reelproj "$(TZ=Asia/Kolkata date +%j)"
else
  python3 styreel.py "$JSON" reelproj "$STYLE"
fi
export DO_NOT_TRACK=1 HYPERFRAMES_NO_TELEMETRY=1
export HYPERFRAMES_BROWSER_PATH=${HYPERFRAMES_BROWSER_PATH:-/usr/bin/google-chrome}
(cd reelproj && npx hyperframes render --quality looks -o ../out/freshtechupdates-reel.mp4)
echo "STYLE=$STYLE"
ffprobe -v error -show_entries format=duration:stream=codec_type,width,height -of compact out/freshtechupdates-reel.mp4
