#!/usr/bin/env bash
# v2 setup (Remotion + Remocn renderer). Run once per machine, after ./setup.sh (which installs the free Kokoro voice).
#   ./setup-v2.sh            -> studio/node_modules, ../remocn (component source, MIT), studio/catalog/catalog.json
set -euo pipefail
cd "$(dirname "$0")"
[ -s kokoro-v1.0.onnx ] || ./setup.sh
REMOCN=${REMOCN_DIR:-$(cd .. && pwd)/remocn}
if [ ! -d "$REMOCN/registry-artifacts" ]; then
  GIT_LFS_SKIP_SMUDGE=1 git clone -q --depth 1 https://github.com/Remocn/remocn "$REMOCN"
fi
(cd studio && npm install --no-audit --no-fund --loglevel=error)
python3 studio/tools/catalog.py build --repo "$REMOCN"
python3 studio/tools/remocn_add.py --repo "$REMOCN" --fonts-only >/dev/null || true
echo "REMOCN_DIR=$REMOCN"
echo "setup-v2 ok"
