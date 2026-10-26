#!/usr/bin/env bash
# Re-download the public TCM-SD release used by this project.
# Primary public page: https://github.com/Borororo/ZY-BERT
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${ROOT}/data/raw/TCM-SD"
mkdir -p "${DEST}"
cd "${DEST}"

BASE="https://raw.githubusercontent.com/Borororo/ZY-BERT/main"
curl -fsSL -o TCM_SD_train_dev.zip "${BASE}/TCM_SD_train_dev.zip"
curl -fsSL -o test.json "${BASE}/test.json"
curl -fsSL -o TCM_Data_Sample.zip "${BASE}/TCM%20Data%20Sample.zip"
curl -fsSL -o UPSTREAM_README.md "${BASE}/README.md"
curl -fsSL -o UPSTREAM_LICENSE_MIT_SOFTWARE.txt "${BASE}/LICENSE"
unzip -qo TCM_SD_train_dev.zip
unzip -qo TCM_Data_Sample.zip
echo "TCM-SD files are in ${DEST}"
ls -lh train.json dev.json test.json syndrome_vocab.txt
