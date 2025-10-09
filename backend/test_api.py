#!/usr/bin/env python3
"""Simple test script to check API functionality"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

# Test Google Drive sync
print("Testing Google Drive sync...")
try:
    # Update the Google Drive path to the correct one
    os.environ['GOOGLE_DRIVE_PATH'] = '/Users/mikail/Library/CloudStorage/GoogleDrive-mikail@netzinformatique.fr/Drive\'ım'
    
    from google_drive_sync import GoogleDriveSync
    sync = GoogleDriveSync()
    
    print(f"Google Drive path: {sync.drive_path}")
    print(f"Path exists: {sync.drive_path.exists()}")
    
    if sync.drive_path.exists():
        # Scan documents
        documents = sync.scan_documents()
        print(f"Found {len(documents)} documents")
        
        for doc in documents[:5]:  # Show first 5
            print(f"  - {doc.metadata['file_name']} ({doc.metadata['file_type']})")
    else:
        print("Google Drive path does not exist!")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50 + "\n")

# Test PennyLane ingestion
print("Testing PennyLane ingestion...")
try:
    from pennylane_ingestion import PennyLaneIngestion
    ingestion = PennyLaneIngestion()
    
    print("PennyLane ingestion initialized successfully")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()