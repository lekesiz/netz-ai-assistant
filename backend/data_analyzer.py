import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple
import mimetypes
from collections import defaultdict

logger = logging.getLogger(__name__)

class DataAnalyzer:
    """Analyze Google Drive data for NETZ Informatique"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.file_stats = defaultdict(int)
        self.file_extensions = defaultdict(int)
        self.important_dirs = []
        self.documents = []
        
    def analyze_directory(self) -> Dict:
        """Analyze the entire directory structure"""
        logger.info(f"Starting analysis of: {self.base_path}")
        
        total_size = 0
        file_count = 0
        
        for root, dirs, files in os.walk(self.base_path):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if file.startswith('.'):
                    continue
                    
                file_path = Path(root) / file
                file_count += 1
                
                try:
                    file_size = file_path.stat().st_size
                    total_size += file_size
                    
                    # Get file extension
                    ext = file_path.suffix.lower()
                    self.file_extensions[ext] += 1
                    
                    # Categorize files
                    self._categorize_file(file_path, ext)
                    
                except Exception as e:
                    logger.warning(f"Error processing {file_path}: {e}")
        
        # Identify important directories
        self._identify_important_dirs()
        
        return {
            "total_files": file_count,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_extensions": dict(self.file_extensions),
            "file_categories": dict(self.file_stats),
            "important_directories": self.important_dirs,
            "document_count": len(self.documents)
        }
    
    def _categorize_file(self, file_path: Path, ext: str):
        """Categorize files by type"""
        # Documents
        if ext in ['.pdf', '.doc', '.docx', '.txt', '.odt']:
            self.file_stats['documents'] += 1
            self.documents.append(str(file_path))
        
        # Spreadsheets
        elif ext in ['.xls', '.xlsx', '.csv', '.ods']:
            self.file_stats['spreadsheets'] += 1
            self.documents.append(str(file_path))
        
        # Presentations
        elif ext in ['.ppt', '.pptx', '.odp']:
            self.file_stats['presentations'] += 1
            
        # Images
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.bmp']:
            self.file_stats['images'] += 1
            
        # Archives
        elif ext in ['.zip', '.rar', '.7z', '.tar', '.gz']:
            self.file_stats['archives'] += 1
            
        # Code/Config
        elif ext in ['.py', '.js', '.json', '.yaml', '.yml', '.md', '.sh']:
            self.file_stats['code_config'] += 1
            
        # Other
        else:
            self.file_stats['other'] += 1
    
    def _identify_important_dirs(self):
        """Identify important directories for the company"""
        important_keywords = [
            'NETZ INFORMATIQUE', 'MSS', 'Documents', 'Facture', 
            'Contrat', 'Client', 'Formation', 'BILAN'
        ]
        
        for root, dirs, files in os.walk(self.base_path):
            dir_path = Path(root)
            dir_name = dir_path.name
            
            # Check if directory name contains important keywords
            for keyword in important_keywords:
                if keyword.lower() in dir_name.lower():
                    self.important_dirs.append({
                        'path': str(dir_path),
                        'name': dir_name,
                        'file_count': len(files)
                    })
                    break
    
    def get_trainable_documents(self, limit: int = 100) -> List[str]:
        """Get list of documents suitable for training"""
        # Prioritize certain file types
        priority_extensions = ['.pdf', '.docx', '.txt']
        
        prioritized_docs = []
        other_docs = []
        
        for doc in self.documents:
            if any(doc.endswith(ext) for ext in priority_extensions):
                prioritized_docs.append(doc)
            else:
                other_docs.append(doc)
        
        # Return prioritized documents first
        all_docs = prioritized_docs + other_docs
        return all_docs[:limit]
    
    def save_analysis(self, output_path: str):
        """Save analysis results to file"""
        analysis = self.analyze_directory()
        analysis['trainable_documents'] = self.get_trainable_documents()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Analysis saved to: {output_path}")
        return analysis

if __name__ == "__main__":
    # Test the analyzer
    google_drive_path = "/Users/mikail/Library/CloudStorage/GoogleDrive-mikail@netzinformatique.fr/Diğer bilgisayarlar/Mon ordinateur/Commun"
    
    analyzer = DataAnalyzer(google_drive_path)
    results = analyzer.save_analysis("data_analysis.json")
    
    print(f"Analysis Complete:")
    print(f"- Total files: {results['total_files']}")
    print(f"- Total size: {results['total_size_mb']} MB")
    print(f"- Document count: {results['document_count']}")
    print(f"- Important directories: {len(results['important_directories'])}")