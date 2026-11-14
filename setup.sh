#!/usr/bin/env bash
# One-time setup per run: Node deps, free offline voice (Kokoro), browser check.
set -euo pipefail
cd "$(dirname "$0")"
npm install --no-audit --no-fund --loglevel=error
pip install --break-system-packages -q kokoro-onnx soundfile numpy playwright
REL=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0
[ -s kokoro-v1.0.onnx ] || curl -sSL -o kokoro-v1.0.onnx "$REL/kokoro-v1.0.onnx"
[ -s voices-v1.0.bin ] || curl -sSL -o voices-v1.0.bin "$REL/voices-v1.0.bin"
if [ ! -x "${CHROME_PATH:-/usr/bin/google-chrome}" ]; then
  python3 -m playwright install chromium >/dev/null
  echo "NOTE: /usr/bin/google-chrome missing; installed Playwright Chromium. Set CHROME_PATH and HYPERFRAMES_BROWSER_PATH to its binary."
fi
command -v ffmpeg >/dev/null || echo "WARNING: ffmpeg not found"
echo "setup ok"
