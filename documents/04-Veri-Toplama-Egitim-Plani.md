# NETZ Informatique - Veri Toplama ve Eğitim Süreci Planı

## 🎯 Hedef
NETZ Informatique'in tüm kurumsal bilgilerini toplayıp, yapay zeka modelini şirkete özel olarak eğitmek.

## 📊 Veri Kaynakları

### 1. Google Workspace Verileri

#### A. Google Drive
```python
# Toplanacak veri tipleri:
- PDF dokümanları (teknik dökümanlar, prosedürler)
- Word/Excel dosyaları (raporlar, tablolar)
- Sunumlar (şirket prezentasyonları)
- Görüntüler (diyagramlar, şemalar)
- Video içerikler (eğitim videoları)

# Tahmini boyut: 500GB+
```

#### B. Gmail
```python
# E-posta kategorileri:
- Müşteri yazışmaları
- Teknik destek biletleri  
- Satış süreçleri
- İç iletişim
- Proje yönetimi

# Tahmini miktar: 100,000+ e-posta
```

#### C. Google Calendar
- Toplantı notları
- Proje timeline'ları
- Bakım takvimleri

### 2. Web Verileri
- netzinformatique.com içeriği
- Blog yazıları
- Hizmet açıklamaları
- Referanslar ve portfolyo

### 3. İç Sistemler
- CRM verileri
- Ticket yönetim sistemi
- Muhasebe kayıtları (anonim)
- Envanter yönetimi

## 🔄 Veri Toplama Pipeline

### Phase 1: Google Drive Entegrasyonu

```python
# google_drive_connector.py
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

class GoogleDriveCollector:
    def __init__(self, credentials_path):
        self.creds = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        self.service = build('drive', 'v3', credentials=self.creds)
    
    def list_all_files(self, folder_id=None):
        """Tüm dosyaları recursive olarak listele"""
        query = f"'{folder_id}' in parents" if folder_id else None
        results = []
        page_token = None
        
        while True:
            response = self.service.files().list(
                q=query,
                pageSize=1000,
                fields="nextPageToken, files(id, name, mimeType, size)",
                pageToken=page_token
            ).execute()
            
            results.extend(response.get('files', []))
            page_token = response.get('nextPageToken')
            
            if not page_token:
                break
                
        return results
    
    def download_file(self, file_id, file_name, mime_type):
        """Dosyayı indir ve dönüştür"""
        if 'google-apps' in mime_type:
            # Google formatlarını dışa aktar
            export_mime_type = self.get_export_format(mime_type)
            request = self.service.files().export_media(
                fileId=file_id,
                mimeType=export_mime_type
            )
        else:
            # Binary dosyaları indir
            request = self.service.files().get_media(fileId=file_id)
        
        # Dosyayı kaydet
        with open(f"data/raw/{file_name}", "wb") as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
```

### Phase 2: Gmail Veri Toplama

```python
# gmail_connector.py
import base64
from datetime import datetime

class GmailCollector:
    def __init__(self, credentials_path):
        self.creds = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/gmail.readonly']
        )
        self.service = build('gmail', 'v1', credentials=self.creds)
    
    def fetch_messages(self, query='', max_results=1000):
        """E-postaları topla"""
        messages = []
        page_token = None
        
        while len(messages) < max_results:
            response = self.service.users().messages().list(
                userId='me',
                q=query,
                pageToken=page_token,
                maxResults=min(500, max_results - len(messages))
            ).execute()
            
            messages.extend(response.get('messages', []))
            page_token = response.get('nextPageToken')
            
            if not page_token:
                break
        
        return messages
    
    def process_message(self, msg_id):
        """E-posta içeriğini işle"""
        message = self.service.users().messages().get(
            userId='me',
            id=msg_id,
            format='full'
        ).execute()
        
        # Metadata çıkar
        headers = message['payload'].get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        from_email = next((h['value'] for h in headers if h['name'] == 'From'), '')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
        
        # İçeriği çıkar
        body = self.extract_body(message['payload'])
        
        return {
            'id': msg_id,
            'subject': subject,
            'from': from_email,
            'date': date,
            'body': body
        }
```

### Phase 3: Web Scraping

```python
# web_scraper.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class WebScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.visited_urls = set()
        self.session = requests.Session()
    
    def scrape_website(self):
        """Web sitesinin tamamını tara"""
        to_visit = [self.base_url]
        scraped_data = []
        
        while to_visit:
            url = to_visit.pop(0)
            if url in self.visited_urls:
                continue
                
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # İçeriği çıkar
                    page_data = {
                        'url': url,
                        'title': soup.find('title').text if soup.find('title') else '',
                        'content': self.extract_text(soup),
                        'meta_description': self.get_meta_description(soup)
                    }
                    scraped_data.append(page_data)
                    
                    # Yeni linkler bul
                    for link in soup.find_all('a', href=True):
                        absolute_url = urljoin(url, link['href'])
                        if self.is_valid_url(absolute_url):
                            to_visit.append(absolute_url)
                
                self.visited_urls.add(url)
                
            except Exception as e:
                print(f"Error scraping {url}: {e}")
        
        return scraped_data
```

## 🧹 Veri Temizleme ve Hazırlama

### 1. Text Extraction Pipeline

```python
# text_processor.py
import pytesseract
from pdf2image import convert_from_path
import docx
import pandas as pd

class DocumentProcessor:
    def process_document(self, file_path):
        """Dosya tipine göre text çıkarma"""
        ext = file_path.split('.')[-1].lower()
        
        if ext == 'pdf':
            return self.extract_pdf_text(file_path)
        elif ext in ['docx', 'doc']:
            return self.extract_word_text(file_path)
        elif ext in ['xlsx', 'xls']:
            return self.extract_excel_text(file_path)
        elif ext in ['png', 'jpg', 'jpeg']:
            return self.extract_image_text(file_path)
        else:
            return self.extract_plain_text(file_path)
    
    def extract_pdf_text(self, pdf_path):
        """PDF'den text çıkar"""
        text = ""
        try:
            # OCR gerekebilir
            pages = convert_from_path(pdf_path)
            for page in pages:
                text += pytesseract.image_to_string(page, lang='fra')
        except:
            # Fallback to pypdf
            import PyPDF2
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
        return text
```

### 2. Data Structuring

```python
# data_structurer.py
class DataStructurer:
    def structure_company_data(self, raw_data):
        """Ham veriyi yapılandır"""
        structured = {
            'company_info': self.extract_company_info(raw_data),
            'services': self.extract_services(raw_data),
            'procedures': self.extract_procedures(raw_data),
            'faqs': self.extract_faqs(raw_data),
            'contacts': self.extract_contacts(raw_data),
            'projects': self.extract_projects(raw_data)
        }
        return structured
    
    def create_training_dataset(self, structured_data):
        """Fine-tuning için dataset oluştur"""
        training_examples = []
        
        # Soru-cevap çiftleri oluştur
        for category, data in structured_data.items():
            examples = self.generate_qa_pairs(category, data)
            training_examples.extend(examples)
        
        return training_examples
```

## 🎓 Model Eğitim Stratejisi

### 1. Base Model Fine-tuning

```bash
# Fine-tuning parametreleri
MODEL_NAME="mistral-7b-instruct"
DATASET="netz_training_data.jsonl"
OUTPUT_DIR="models/netz-mistral-v1"

# LoRA configuration
LORA_R=16
LORA_ALPHA=32
LORA_DROPOUT=0.05

# Training hyperparameters
EPOCHS=3
BATCH_SIZE=4
LEARNING_RATE=2e-5
MAX_LENGTH=2048
```

### 2. RAG (Retrieval Augmented Generation) Setup

```python
# rag_pipeline.py
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Qdrant
from langchain.chains import RetrievalQA

class RAGPipeline:
    def __init__(self):
        # Embedding model (Fransızca optimize)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="dangvantuan/sentence-camembert-base",
            model_kwargs={'device': 'cuda'}
        )
        
        # Vector store
        self.vector_store = Qdrant(
            collection_name="netz_knowledge",
            embeddings=self.embeddings,
            url="http://localhost:6333"
        )
    
    def index_documents(self, documents):
        """Dokümanları vektör veritabanına ekle"""
        texts = [doc['content'] for doc in documents]
        metadatas = [{'source': doc['source'], 'type': doc['type']} for doc in documents]
        
        self.vector_store.add_texts(
            texts=texts,
            metadatas=metadatas
        )
    
    def create_qa_chain(self, llm):
        """QA chain oluştur"""
        retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True
        )
        
        return qa_chain
```

## 🔄 Otomatik Güncelleme Sistemi

### 1. Scheduled Data Sync

```python
# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
import logging

class DataUpdateScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.logger = logging.getLogger(__name__)
    
    def setup_jobs(self):
        """Periyodik görevleri ayarla"""
        # Günlük Google Drive sync
        self.scheduler.add_job(
            func=self.sync_google_drive,
            trigger="cron",
            hour=2,  # 02:00
            id='drive_sync'
        )
        
        # Haftalık Gmail sync
        self.scheduler.add_job(
            func=self.sync_gmail,
            trigger="cron",
            day_of_week='sun',
            hour=3,
            id='gmail_sync'
        )
        
        # Aylık web scraping
        self.scheduler.add_job(
            func=self.scrape_website,
            trigger="cron",
            day=1,
            hour=4,
            id='web_scrape'
        )
        
        # Model retraining (quarterly)
        self.scheduler.add_job(
            func=self.retrain_model,
            trigger="cron",
            month='*/3',
            day=15,
            hour=1,
            id='model_retrain'
        )
```

### 2. Incremental Learning

```python
# incremental_learning.py
class IncrementalLearner:
    def __init__(self, base_model_path):
        self.base_model_path = base_model_path
        self.new_data_buffer = []
    
    def add_new_example(self, example):
        """Yeni örnek ekle"""
        self.new_data_buffer.append(example)
        
        # Buffer dolduğunda mini-batch training
        if len(self.new_data_buffer) >= 100:
            self.mini_batch_train()
    
    def mini_batch_train(self):
        """Mini-batch ile güncelleme"""
        # LoRA adapter'ı güncelle
        update_lora_adapter(
            base_model=self.base_model_path,
            new_examples=self.new_data_buffer,
            learning_rate=1e-6  # Düşük LR
        )
        self.new_data_buffer = []
```

## 📊 Veri Güvenliği ve Gizlilik

### 1. Anonimleştirme
```python
# Kişisel verileri maskele
- E-posta adresleri → [EMAIL]
- Telefon numaraları → [PHONE]
- Kredi kartı → [CC_NUMBER]
- Müşteri isimleri → [CUSTOMER_NAME]
```

### 2. Erişim Kontrolü
```python
# Veri erişim seviyeleri
LEVELS = {
    'public': ['company_info', 'services'],
    'employee': ['procedures', 'internal_docs'],
    'manager': ['financial_reports', 'hr_docs'],
    'admin': ['*']
}
```

---
*Son güncelleme: 2025-01-09*