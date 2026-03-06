#!/usr/bin/env bash
set -euo pipefail

python3 -m pip install -r requirements.txt
pyinstaller --noconfirm --onefile --windowed --name agente_uniformes src/app.py

echo "Build finalizado. Executável em: dist/agente_uniformes"
