#!/usr/bin/env bash
# Trending-explainer Short/Reel (one hot topic in 3 beats: what it is, why now, what it means for you).
# Usage: ./make_trend.sh trend.json [comic|paper|blueprint]
#   -> out/trend-reel.mp4 + out/trend-cover.png + out/trend-short.txt
# With no style given, the style rotates by weekday but one step ahead of the daily Short,
# so the two Shorts posted on the same day never look the same:
#   daily:  Mon/Wed/Fri/Sun comic · Tue/Thu paper · Sat blueprint
#   trend:  Mon/Wed/Fri paper · Tue/Thu/Sat comic · Sun blueprint
set -euo pipefail
cd "$(dirname "$0")"
JSON=$(realpath "${1:?usage: make_trend.sh trend.json [style]}")
STYLE=${2:-}
if [ -z "$STYLE" ]; then
  case $(TZ=Asia/Kolkata date +%u) in
    1|3|5) STYLE=paper ;;
    2|4|6) STYLE=comic ;;
    7) STYLE=blueprint ;;
  esac
fi
python3 -c "import json,sys; d=json.load(open(sys.argv[1])); assert d.get('mode')=='explainer', 'trend.json needs \"mode\": \"explainer\"'; assert len(d['stories'])==3, 'trend.json needs exactly 3 stories (beats)'" "$JSON"
rm -rf trendproj && mkdir -p out
python3 styreel.py "$JSON" trendproj "$STYLE"
export DO_NOT_TRACK=1 HYPERFRAMES_NO_TELEMETRY=1
export HYPERFRAMES_BROWSER_PATH=${HYPERFRAMES_BROWSER_PATH:-${CHROME_PATH:-/usr/bin/google-chrome}}
(cd trendproj && npx hyperframes render --quality looks -o ../out/trend-reel.mp4)
python3 thumbs.py short "$JSON" trend   # out/trend-cover.png + out/trend-short.txt
echo "STYLE=$STYLE"
ffprobe -v error -show_entries format=duration:stream=codec_type,width,height -of compact out/trend-reel.mp4
