# 🚀 NETZ AI - Kullanım Klavuzu

## 📋 İçindekiler
1. [Kurulum](#kurulum)
2. [Yerel Geliştirme](#yerel-geliştirme)
3. [API Kullanımı](#api-kullanımı)
4. [Browser Testi](#browser-testi)
5. [Özellikler](#özellikler)
6. [Sorun Giderme](#sorun-giderme)
7. [Gelişmiş Kullanım](#gelişmiş-kullanım)

## 🔧 Kurulum

### Gereksinimler
- Python 3.11+
- Node.js 18+ (opsiyonel, frontend için)
- Ollama (LLM sunucusu)
- Git

### 1. Repository'yi İndirin
```bash
git clone https://github.com/lekesiz/netzinformatique.git
cd netzinformatique/NETZ-AI-Project
```

### 2. Python Sanal Ortamı Oluşturun
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate     # Windows
```

### 3. Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### 4. Ollama'yı Kurun ve Başlatın
```bash
# Ollama kurulumu (macOS)
brew install ollama
ollama serve

# Model indirin
ollama pull mistral:latest
```

### 5. Çevre Değişkenlerini Ayarlayın
```bash
cp .env.example .env
# .env dosyasını düzenleyin
```

## 🏃‍♂️ Yerel Geliştirme

### API Sunucusunu Başlatın
```bash
cd backend
uvicorn simple_api:app --reload --host 0.0.0.0 --port 8000
```

### Sağlık Kontrolü
```bash
curl http://localhost:8000/health
```

**Beklenen Yanıt:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-10T10:30:00Z",
  "mode": "university_level"
}
```

## 🌐 API Kullanımı

### Temel Chat Endpoint
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Bonjour, qu'\''est-ce que NETZ Informatique?"}
    ]
  }'
```

### API Dokümantasyonu
Tarayıcınızda açın: http://localhost:8000/docs

### Mevcut Endpoint'ler
- `GET /health` - Sistem durumu
- `GET /ready` - Hazırlık durumu
- `POST /api/chat` - Chat endpoint
- `GET /api/models` - Mevcut modeller
- `POST /api/search` - RAG arama
- `GET /docs` - API dokümantasyonu

## 🖥️ Browser Testi

### 1. Test Sayfasını Açın
```bash
# Proje kök dizininde
open browser-test.html
# veya tarayıcınızda file:///path/to/browser-test.html
```

### 2. Test Senaryoları

#### Temel Testler
- ✅ "Bonjour" - Karşılama mesajı
- ✅ "Qu'est-ce que NETZ Informatique?" - Şirket bilgisi
- ✅ "Quels sont vos tarifs?" - Fiyat bilgileri
- ✅ "Proposez-vous des formations?" - Eğitim hizmetleri

#### Teknik Destek Testleri
- ✅ "Mon ordinateur est lent" - Teknik yardım
- ✅ "J'ai un virus" - Güvenlik sorunu
- ✅ "Comment sauvegarder mes données?" - Yedekleme

#### İş Testleri
- ✅ "Je suis une entreprise" - Kurumsal hizmetler
- ✅ "Contrat de maintenance" - Bakım sözleşmeleri
- ✅ "Formation sur site" - Yerinde eğitim

### 3. Beklenen Sonuçlar
- ✅ Fransızca yanıtlar
- ✅ NETZ-spesifik bilgiler
- ✅ Profesyonel ton
- ✅ İletişim bilgileri dahil
- ✅ 2-5 saniye yanıt süresi

## ⚡ Özellikler

### 🤖 AI Yetenekleri
- **Çok Dilli**: Fransızca, İngilizce, Türkçe, Almanca
- **Bağlam Farkındalığı**: Konuşma geçmişini hatırlar
- **Teknik Uzman**: Bilgisayar sorunları ve çözümleri
- **Satış Desteği**: Hizmet önerileri ve fiyatlandırma

### 📚 Bilgi Tabanı
- **NETZ Hizmetleri**: Tam hizmet kataloğu
- **Fiyat Listesi**: Güncel tarife bilgileri
- **Teknik Bilgi**: Sorun giderme rehberleri
- **Eğitim Programları**: QUALIOPI sertifikalı kurslar

### 🔒 Güvenlik
- **Rate Limiting**: İsteklerin sınırlandırılması
- **Input Validation**: Girdi doğrulama
- **CORS Protection**: Cross-origin güvenlik
- **Error Handling**: Güvenli hata yönetimi

### 📊 Monitoring
- **Health Checks**: Sistem durumu izleme
- **Performance Metrics**: Performans metrikleri
- **Request Logging**: İstek kayıtları
- **Error Tracking**: Hata takibi

## 🔧 Sorun Giderme

### API Başlamıyor
```bash
# Port kontrolü
lsof -i :8000

# Ollama durumu
ollama list

# Log kontrolü
tail -f logs/api.log
```

### Slow Response (Yavaş Yanıt)
```bash
# Model kontrolü
ollama ps

# Sistem kaynakları
htop
```

### Chat Çalışmıyor
1. ✅ API health check yapın
2. ✅ Browser console'da hata var mı?
3. ✅ CORS ayarları doğru mu?
4. ✅ Network connectivity var mı?

### Model Bulunamıyor
```bash
# Modelleri listele
ollama list

# Mistral'ı indir
ollama pull mistral:latest

# Yeniden başlat
pkill ollama && ollama serve
```

## 🚀 Gelişmiş Kullanım

### Production Deployment
```bash
# Docker ile
docker-compose up -d

# Manuel deployment
./scripts/deploy.sh production
```

### Custom Training
```bash
# PennyLane entegrasyonu
python pennylane_enhanced_integration.py

# Google Drive import
python google_drive_integration.py

# Web knowledge
python netz_web_scraper.py

# Komplet training
python train_ai_complete.py
```

### Monitoring & Analytics
```bash
# Prometheus metrics
curl http://localhost:9090/metrics

# Health dashboard
curl http://localhost:8000/stats

# Performance test
python ai_quality_tester.py
```

### Backup & Recovery
```bash
# Veri yedekleme
./scripts/backup.sh

# Database export
./scripts/export_data.sh

# Geri yükleme
./scripts/restore.sh backup_file.tar.gz
```

## 📋 Checklist - Production Hazırlığı

### ✅ Temel Kurulum
- [ ] Python environment aktif
- [ ] Tüm dependencies yüklü
- [ ] Ollama çalışıyor
- [ ] API başlıyor
- [ ] Health check geçiyor

### ✅ Fonksiyonellik
- [ ] Chat endpoint çalışıyor
- [ ] Fransızca yanıtlar
- [ ] NETZ bilgileri doğru
- [ ] Teknik sorular yanıtlanıyor
- [ ] İletişim bilgileri veriliyor

### ✅ Performance
- [ ] Yanıt süresi < 5 saniye
- [ ] Concurrent users destekli
- [ ] Memory usage normal
- [ ] Error rate < 1%

### ✅ Güvenlik
- [ ] Rate limiting aktif
- [ ] Input validation çalışıyor
- [ ] CORS ayarları doğru
- [ ] Sensitive data korunuyor

### ✅ Monitoring
- [ ] Logs yazılıyor
- [ ] Metrics toplanıyor
- [ ] Health checks çalışıyor
- [ ] Alerts ayarlanmış

## 🆘 Destek

### Hızlı Komutlar
```bash
# Status check
make status

# Restart all
make restart

# View logs
make logs

# Run tests
make test

# Deploy
make deploy
```

### Debug Mode
```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
uvicorn simple_api:app --reload
```

### Logs
```bash
# API logs
tail -f logs/api.log

# Error logs  
tail -f logs/error.log

# Access logs
tail -f logs/access.log
```

---

## 📞 İletişim

**Teknik Destek:**
- 📧 Email: tech@netzinformatique.fr
- 📱 Telefon: 07 67 74 49 03
- 🌐 Web: www.netzinformatique.fr

**Repository:**
- 🔗 GitHub: https://github.com/lekesiz/netzinformatique
- 📖 Wiki: https://github.com/lekesiz/netzinformatique/wiki
- 🐛 Issues: https://github.com/lekesiz/netzinformatique/issues

---

*Son Güncelleme: 2025-01-10*
*Versiyon: 2.0.0*