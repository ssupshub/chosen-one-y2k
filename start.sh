#!/bin/bash
echo ""
echo " chosen-one-y2k :: Starting Backend"
echo " ===================================="
echo ""

cd "$(dirname "$0")/backend"

if ! command -v python3 &>/dev/null; then
    echo " ERROR: python3 not found. Install Python 3 from python.org"
    exit 1
fi

echo " Installing dependencies..."
pip3 install -r requirements.txt --quiet --break-system-packages 2>/dev/null \
  || pip3 install -r requirements.txt --quiet

echo ""
echo " Backend starting at http://localhost:5000"
echo " Open index.html in your browser separately."
echo " Press Ctrl+C to stop."
echo ""

python3 app.py
