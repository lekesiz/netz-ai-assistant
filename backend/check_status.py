#!/usr/bin/env python3
"""Simple status check without heavy dependencies"""
import os
import json
from pathlib import Path
from datetime import datetime

print("=== NETZ AI Backend Status Check ===\n")

# 1. Check Google Drive path
google_drive_paths = [
    '/Users/mikail/Library/CloudStorage/GoogleDrive-mikail@netzinformatique.fr/Drive\'ım',
    '/Users/mikail/Library/CloudStorage/GoogleDrive-mikail@netzinformatique.fr/Mon Drive',
    '/Users/mikail/Library/CloudStorage/GoogleDrive-mikail@netzinformatique.fr/My Drive'
]

print("1. Google Drive Status:")
google_drive_found = False
for path in google_drive_paths:
    if Path(path).exists():
        print(f"   ✓ Found: {path}")
        google_drive_found = True
        # Count documents
        try:
            doc_count = 0
            for ext in ['.txt', '.md', '.pdf', '.doc', '.docx', '.json', '.csv']:
                doc_count += len(list(Path(path).rglob(f'*{ext}')))
            print(f"     - Document count (estimated): {doc_count}")
        except Exception as e:
            print(f"     - Error counting documents: {e}")
        break

if not google_drive_found:
    print("   ✗ No Google Drive folder found")

# 2. Check data directory
print("\n2. Data Directory Status:")
data_dir = Path("data")
if data_dir.exists():
    print(f"   ✓ Data directory exists")
    # Check for status files
    status_file = data_dir / "ingestion_status.json"
    if status_file.exists():
        print("   ✓ Ingestion status file found")
        try:
            with open(status_file, 'r') as f:
                status = json.load(f)
                print(f"     - Sources tracked: {list(status.keys())}")
        except Exception as e:
            print(f"     - Error reading status: {e}")
    else:
        print("   ✗ No ingestion status file")
else:
    print("   ✗ Data directory not found")
    
# 3. Check environment variables
print("\n3. Environment Variables:")
env_vars = ['PENNYLANE_API_TOKEN', 'PENNYLANE_BASE_URL', 'GOOGLE_DRIVE_PATH', 'OPENAI_API_KEY']
for var in env_vars:
    value = os.getenv(var)
    if value:
        if 'token' in var.lower() or 'key' in var.lower():
            print(f"   ✓ {var}: ****** (hidden)")
        else:
            print(f"   ✓ {var}: {value[:50]}..." if len(value) > 50 else f"   ✓ {var}: {value}")
    else:
        print(f"   ✗ {var}: Not set")

# 4. Check .env file
print("\n4. Configuration File:")
env_file = Path(".env")
if env_file.exists():
    print("   ✓ .env file found")
    # Count configured services
    with open(env_file, 'r') as f:
        lines = f.readlines()
        configured = [line.split('=')[0] for line in lines if '=' in line and not line.startswith('#')]
        print(f"     - Configured variables: {len(configured)}")
else:
    print("   ✗ No .env file found")

print("\n=== End of Status Check ===")