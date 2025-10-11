#\!/bin/bash

echo "=== NETZ AI Backend Status Check (Shell) ==="
echo

# Check Google Drive
echo "1. Google Drive Status:"
GDRIVE_PATH="/Users/mikail/Library/CloudStorage/GoogleDrive-mikail@netzinformatique.fr/Drive'ım"
if [ -d "$GDRIVE_PATH" ]; then
    echo "   ✓ Google Drive folder exists: $GDRIVE_PATH"
    # Count documents
    DOC_COUNT=$(find "$GDRIVE_PATH" -type f \( -name "*.txt" -o -name "*.md" -o -name "*.pdf" -o -name "*.doc" -o -name "*.docx" -o -name "*.json" -o -name "*.csv" \) 2>/dev/null | wc -l | tr -d ' ')
    echo "   ✓ Document count: $DOC_COUNT"
else
    echo "   ✗ Google Drive folder not found"
fi

echo
echo "2. Data Directory:"
if [ -d "data" ]; then
    echo "   ✓ Data directory exists"
    ls -la data/ | head -5
else
    echo "   ✗ Data directory not found"
fi

echo
echo "3. Environment File:"
if [ -f ".env" ]; then
    echo "   ✓ .env file exists"
    echo "   Variables configured:"
    grep -E "^[A-Z_]+=" .env | cut -d= -f1 | sed 's/^/     - /'
else
    echo "   ✗ .env file not found"
fi

echo
echo "=== End of Status Check ==="
