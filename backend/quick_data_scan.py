import os
from pathlib import Path
import json

def quick_scan(base_path: str, max_depth: int = 3):
    """Quick scan of top-level directories"""
    base = Path(base_path)
    results = {
        "top_directories": [],
        "key_files": [],
        "stats": {
            "pdf_count": 0,
            "doc_count": 0,
            "xls_count": 0,
            "total_files": 0
        }
    }
    
    # Scan top-level directories
    for item in base.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            file_count = sum(1 for _ in item.rglob('*') if _.is_file())
            results["top_directories"].append({
                "name": item.name,
                "path": str(item),
                "file_count": file_count
            })
    
    # Quick file type count
    for ext, key in [('.pdf', 'pdf_count'), ('.doc', 'doc_count'), 
                     ('.docx', 'doc_count'), ('.xls', 'xls_count'), 
                     ('.xlsx', 'xls_count')]:
        count = sum(1 for _ in base.rglob(f'*{ext}'))
        results["stats"][key] += count
        results["stats"]["total_files"] += count
    
    # Find key company files
    key_terms = ['KBIS', 'RIB', 'contrat', 'CGV', 'statut']
    for term in key_terms:
        for file in base.rglob(f'*{term}*'):
            if file.is_file() and not file.name.startswith('.'):
                results["key_files"].append({
                    "name": file.name,
                    "path": str(file.relative_to(base))
                })
                if len(results["key_files"]) >= 20:
                    break
    
    return results

if __name__ == "__main__":
    google_drive_path = "/Users/mikail/Library/CloudStorage/GoogleDrive-mikail@netzinformatique.fr/Diğer bilgisayarlar/Mon ordinateur/Commun"
    
    print("Starting quick scan...")
    results = quick_scan(google_drive_path)
    
    # Save results
    with open("quick_data_scan.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nTop Directories Found:")
    for dir_info in results["top_directories"][:10]:
        print(f"- {dir_info['name']} ({dir_info['file_count']} files)")
    
    print(f"\nFile Statistics:")
    print(f"- PDFs: {results['stats']['pdf_count']}")
    print(f"- DOCs: {results['stats']['doc_count']}")
    print(f"- Spreadsheets: {results['stats']['xls_count']}")
    
    print(f"\nKey Company Files Found: {len(results['key_files'])}")
    print("\nScan complete! Results saved to quick_data_scan.json")