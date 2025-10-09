# NETZ AI Assistant - Detaylı Kullanım Kılavuzu 🤖

## 📋 İçindekiler
1. [Sistem Gereksinimleri](#sistem-gereksinimleri)
2. [Kurulum](#kurulum)
3. [Başlatma](#başlatma)
4. [Özellikler](#özellikler)
5. [Kullanım](#kullanım)
6. [Veri Yönetimi](#veri-yönetimi)
7. [API Dokümantasyonu](#api-dokümantasyonu)
8. [Sorun Giderme](#sorun-giderme)
9. [Güvenlik](#güvenlik)
10. [Bakım ve Güncelleme](#bakım-ve-güncelleme)

---

## 🖥️ Sistem Gereksinimleri

### Minimum Gereksinimler
- **İşlemci**: Intel i5/AMD Ryzen 5 veya üzeri
- **RAM**: 8GB (16GB önerilir)
- **Disk**: 50GB boş alan
- **OS**: macOS, Linux, Windows (WSL2)
- **Python**: 3.11+
- **Node.js**: 18+
- **Docker**: 20.10+

### Önerilen Sistem
- **İşlemci**: Apple M1/M2 veya Intel i7/AMD Ryzen 7
- **RAM**: 16GB+
- **Disk**: 100GB+ SSD
- **GPU**: Opsiyonel (NVIDIA CUDA destekli)

---

## 🚀 Kurulum

### 1. Projeyi İndirme
```bash
git clone https://github.com/lekesiz/netz-ai-assistant.git
cd netz-ai-assistant
```

### 2. Python Sanal Ortam Oluşturma
```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Backend Bağımlılıkları
```bash
cd backend
pip install -r requirements.txt
```

### 4. Frontend Bağımlılıkları
```bash
cd ../frontend
npm install
```

### 5. Docker Servisleri
```bash
cd ..
docker-compose up -d
```

### 6. Ollama ve Model Kurulumu
```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Model indirme
ollama pull mistral
```

### 7. Çevre Değişkenleri

**backend/.env**
```env
# Database
DATABASE_URL=postgresql://netz:netz2024@localhost:5432/netz_ai

# Redis
REDIS_URL=redis://localhost:6379

# Qdrant
QDRANT_URL=http://localhost:6333

# API Keys
PENNYLANE_API_KEY=rBJRccXSMapi7yv6nypkInzxU51G-hxSFEacOCTgFZ4
OPENAI_API_KEY=sk-proj-...
GEMINI_API_KEY=AIzaSy...

# Google Drive
GOOGLE_DRIVE_PATH=/Users/mikail/Library/CloudStorage/GoogleDrive-mikail@netzinformatique.fr/Drive'ım
```

**frontend/.env.local**
```env
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_UPLOAD_API_URL=http://localhost:8002
```

---

## ▶️ Başlatma

### 1. Docker Servislerini Başlat
```bash
docker-compose up -d
```

### 2. Backend Servislerini Başlat
```bash
cd backend

# Ana chat API'si
python simple_api.py &

# Belge yükleme API'si
python document_upload_api.py &

# Opsiyonel: Full RAG API
python main.py &
```

### 3. Frontend'i Başlat
```bash
cd ../frontend
npm run dev
```

### 4. Erişim
- **Ana Sayfa**: http://localhost:3000 (veya 3001)
- **Chat**: http://localhost:3000/chat
- **Belge Yükleme**: http://localhost:3000/documents

---

## ✨ Özellikler

### 1. Çoklu Dil Desteği
- 🇫🇷 Fransızca (ana dil)
- 🇹🇷 Türkçe
- 🇬🇧 İngilizce

### 2. Finansal Veri Entegrasyonu
- PennyLane muhasebe sistemi
- Gerçek zamanlı gelir takibi
- Aylık/yıllık raporlar
- Eğitim bazlı gelir analizi

### 3. Belge İşleme
- PDF okuma ve analiz
- Word belgeleri (.docx)
- Excel tabloları (.xlsx)
- Metin dosyaları (.txt, .csv)
- Otomatik içerik çıkarma

### 4. Akıllı Arama
- Vector-based semantic search
- Bağlamsal cevaplar
- Kaynak gösterimi
- Hızlı yanıt süresi

---

## 📱 Kullanım

### Chat Arayüzü

#### Temel Kullanım
1. Chat sayfasına gidin
2. Sorunuzu yazın
3. Enter'a basın veya Gönder butonuna tıklayın

#### Örnek Sorular

**Finansal Sorular**
- "Quel est le chiffre d'affaires d'octobre 2025?"
- "Ekim ayı ciromuz nedir?"
- "What is our annual revenue projection?"

**Eğitim Soruları**
- "Quelle formation rapporte le plus?"
- "En çok kazandıran eğitim hangisi?"
- "Excel eğitimi fiyatı nedir?"

**Şirket Bilgileri**
- "Quel est notre numéro SIRET?"
- "Kaç aktif müşterimiz var?"
- "Adresimiz nedir?"

### Belge Yükleme

#### Web Arayüzü ile
1. Documents sayfasına gidin
2. Dosyaları sürükle-bırak yapın
3. Veya "Dosya Seç" butonunu kullanın
4. Yükleme tamamlanınca AI otomatik güncellenir

#### API ile
```bash
# Tek dosya
curl -X POST http://localhost:8002/api/upload/document \
  -F "file=@/path/to/document.pdf"

# Çoklu dosya
curl -X POST http://localhost:8002/api/upload/multiple \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.docx"
```

---

## 📊 Veri Yönetimi

### Mevcut Veriler

#### Finansal Veriler (2025)
```
Ocak: 8,234€
Şubat: 9,456€
Mart: 7,890€
Nisan: 10,234€
Mayıs: 8,967€
Haziran: 9,123€
Temmuz: 7,456€
Ağustos: 5,234€
Eylül: 11,234€
Ekim: 41,558.85€
Toplam: 119,386.85€
```

#### Eğitim Gelirleri
```
1. Excel: 35,815.85€ (30%)
2. Bilan: 28,500€ (23.9%)
3. Python: 19,000€ (15.9%)
4. AutoCAD: 13,058.85€ (10.9%)
5. WordPress: 11,264€ (9.4%)
```

### Veri Güncelleme

#### Manuel Güncelleme
```python
python load_complete_data.py
python update_detailed_financials.py
```

#### Belge ile Güncelleme
1. Güncel verileri içeren belge hazırlayın
2. Web arayüzünden yükleyin
3. AI otomatik öğrenir

### Veri Silme
```bash
# Belirli bir belgeyi silme
curl -X DELETE http://localhost:8002/api/documents/{file_hash}

# Tüm verileri sıfırlama
python reset_data.py
```

---

## 🔌 API Dokümantasyonu

### Chat API (Port 8001)

#### POST /api/chat
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Votre question ici"
    }
  ],
  "model": "mistral",
  "temperature": 0.7
}
```

**Response:**
```json
{
  "response": "La réponse de l'AI",
  "model": "mistral",
  "timestamp": "2025-01-09T19:00:00.000Z"
}
```

### Upload API (Port 8002)

#### POST /api/upload/document
```bash
curl -X POST http://localhost:8002/api/upload/document \
  -F "file=@document.pdf"
```

#### GET /api/documents/list
```bash
curl http://localhost:8002/api/documents/list
```

#### DELETE /api/documents/{hash}
```bash
curl -X DELETE http://localhost:8002/api/documents/{hash}
```

---

## 🔧 Sorun Giderme

### Sık Karşılaşılan Sorunlar

#### 1. Port Çakışması
```bash
# Hangi portlar kullanımda
lsof -i :3000
lsof -i :8001
lsof -i :8002

# Çözüm: .env.local dosyasında port değiştir
NEXT_PUBLIC_API_URL=http://localhost:8001
```

#### 2. AI Cevap Vermiyor
```bash
# Servisleri kontrol et
ps aux | grep python | grep -E "(simple_api|document_upload)"

# Ollama durumu
ollama list

# Yeniden başlat
pkill -f simple_api.py
python simple_api.py &
```

#### 3. Yanlış Dilde Cevap
```
# Sorunuza dil belirtin
"Türkçe cevapla: ..."
"Réponds en français: ..."
```

#### 4. Docker Hataları
```bash
# Container durumu
docker ps

# Logları kontrol et
docker logs qdrant

# Yeniden başlat
docker-compose restart
```

#### 5. Belge Yükleme Başarısız
- Dosya boyutu <10MB olmalı
- Desteklenen format mı kontrol et
- Upload API'si çalışıyor mu kontrol et

---

## 🔒 Güvenlik

### Veri Güvenliği
- Tüm veriler yerel sunucuda
- Dışarı veri gönderilmez
- Şifreli depolama mümkün

### API Güvenliği
- Localhost only (production için değiştir)
- API key authentication eklenebilir
- Rate limiting yapılabilir

### Hassas Veri Yönetimi
- Kişisel bilgileri yüklemeden önce temizle
- RGPD uyumlu kullanım
- Düzenli yedekleme

---

## 🔄 Bakım ve Güncelleme

### Günlük Bakım
```bash
# Log kontrolü
tail -f backend/simple_api.log
tail -f backend/document_upload.log

# Disk kullanımı
du -sh uploaded_documents/
du -sh processed_documents/
```

### Haftalık Bakım
```bash
# Veritabanı optimizasyonu
docker exec -it postgres psql -U netz -d netz_ai -c "VACUUM ANALYZE;"

# Eski logları temizle
find . -name "*.log" -mtime +7 -delete
```

### Model Güncelleme
```bash
# Yeni model indir
ollama pull mistral:latest

# Mevcut modeli kontrol et
ollama list
```

### Yedekleme
```bash
# Veritabanı yedeği
pg_dump -U netz -h localhost netz_ai > backup_$(date +%Y%m%d).sql

# Belge yedeği
tar -czf documents_backup_$(date +%Y%m%d).tar.gz processed_documents/

# Knowledge base yedeği
cp simple_api_kb.json backups/kb_backup_$(date +%Y%m%d).json
```

---

## 📈 Performans İpuçları

1. **RAM Optimizasyonu**
   - Kullanılmayan servisleri kapat
   - Docker memory limitlerini ayarla

2. **Hız Optimizasyonu**
   - Simple API kullan (daha hızlı)
   - Cache'i etkin tut
   - SSD disk kullan

3. **Model Seçimi**
   - Mistral 7B: Dengeli performans
   - Llama 2: Daha iyi Türkçe
   - Qwen: Çok dilli destek

---

## 🆘 Acil Durumlar

### Sistem Çökmesi
```bash
# Tüm servisleri durdur
docker-compose down
pkill -f python

# Temiz başlat
docker-compose up -d
cd backend && python simple_api.py &
cd ../frontend && npm run dev
```

### Veri Kaybı
```bash
# Son yedekten geri yükle
psql -U netz -h localhost netz_ai < backup_latest.sql
cp backups/kb_backup_latest.json simple_api_kb.json
```

---

## 📞 Destek

**Teknik Destek**: mikail@netzinformatique.fr

**Acil Durumlar**: +33 3 67 31 02 01

**GitHub Issues**: https://github.com/lekesiz/netz-ai-assistant/issues

---

*NETZ INFORMATIQUE - AI ile Geleceği İnşa Ediyoruz*

*Son güncelleme: 9 Ocak 2025*