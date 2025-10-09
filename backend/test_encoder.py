#!/usr/bin/env python3
"""Test if sentence transformer is working"""

try:
    print("Loading sentence transformer...")
    from sentence_transformers import SentenceTransformer
    encoder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    print("✅ Encoder loaded successfully")
    
    test_text = "Test encoding"
    vector = encoder.encode(test_text)
    print(f"✅ Test encoding successful, vector shape: {vector.shape}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()