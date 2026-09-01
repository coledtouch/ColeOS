#!/usr/bin/env bash
# Rebuild Cole-Ciprari-Systems-Architect-Resume.pdf from _src/resume-print.html.
# Needs WeasyPrint — run in WSL (pip install --user --break-system-packages weasyprint);
# Windows-native WeasyPrint can't find Pango. DejaVu fonts come with Ubuntu.
set -euo pipefail
cd "$(dirname "$0")"
WP="${WEASYPRINT:-$HOME/.local/bin/weasyprint}"
command -v "$WP" >/dev/null 2>&1 || WP=weasyprint
"$WP" resume-print.html ../Cole-Ciprari-Systems-Architect-Resume.pdf
echo "wrote ../Cole-Ciprari-Systems-Architect-Resume.pdf"
