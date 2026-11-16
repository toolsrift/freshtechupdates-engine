#!/usr/bin/env bash
# Usage: ./make_episode.sh episode.json [show 1-7]
#   -> out/freshtechupdates-episode.mp4 (16:9 YouTube episode), out/thumbnail.png, out/youtube.txt
# Show rotates by weekday (India time) when not given:
#   1 Mon The Newsroom · 2 Tue The Countdown · 3 Wed Blueprint Lab · 4 Thu Update Arcade
#   5 Fri World Tour · 6 Sat The Classroom · 7 Sun Paper Studio
# Rendering takes ~4 min per minute of video. Run it in the background and watch the log:
#   nohup ./make_episode.sh episode.json > out/episode.log 2>&1 &     (finished when the log says EPISODE_DONE)
set -euo pipefail
cd "$(dirname "$0")"
JSON=$(realpath "${1:?usage: make_episode.sh episode.json [show]}")
SHOW=${2:-$(TZ=Asia/Kolkata date +%u)}
export CHROME_PATH=${CHROME_PATH:-/usr/bin/google-chrome}
rm -rf epproj out/episode-parts && mkdir -p out/episode-parts
python3 longform.py "$JSON" epproj "$SHOW"
export DO_NOT_TRACK=1 HYPERFRAMES_NO_TELEMETRY=1
export HYPERFRAMES_BROWSER_PATH=${HYPERFRAMES_BROWSER_PATH:-$CHROME_PATH}
TOTAL=$(grep -o 'data-composition-id="main" data-start="0" data-duration="[0-9.]*"' epproj/index.html | grep -o '[0-9.]*"$' | tr -d '"')
SEG=60
# Render in 60 s parts (faster than one long render on small machines), then join and add the audio.
N=$(python3 -c "import math;print(math.ceil($TOTAL/$SEG))")
: > out/episode-parts/list.txt
for ((k=0; k<N; k++)); do
  S=$((k*SEG)); E=$(python3 -c "print(min($TOTAL, $(( (k+1)*SEG ))))")
  P=$(printf "out/episode-parts/part%02d.mp4" "$k")
  for try in 1 2; do
    (cd epproj && npx hyperframes render --quality looks --start "$S" --end "$E" -o "../$P" > ../out/episode-parts/render.log 2>&1) && break
    echo "part $k failed (try $try)"; tail -5 out/episode-parts/render.log
  done
  echo "file '$(basename "$P")'" >> out/episode-parts/list.txt
  echo "PART $((k+1))/$N done"
done
ffmpeg -v error -y -f concat -safe 0 -i out/episode-parts/list.txt -an -c:v copy out/episode-parts/video.mp4
ffmpeg -v error -y -i out/episode-parts/video.mp4 -i epproj/assets/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest \
  -movflags +faststart out/freshtechupdates-episode.mp4
ffprobe -v error -show_entries format=duration:stream=codec_type,width,height -of compact out/freshtechupdates-episode.mp4
echo "EPISODE_DONE show=$SHOW"
