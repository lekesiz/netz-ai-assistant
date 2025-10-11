# 🚀 NETZ AI Assistant - Detaylı Kullanım Kılavuzu

## 📋 İçindekiler
1. [Sistem Gereksinimleri](#sistem-gereksinimleri)
2. [Kurulum](#kurulum)
3. [Servisleri Başlatma](#servisleri-başlatma)
4. [API Kullanımı](#api-kullanımı)
5. [Web Arayüzü Kullanımı](#web-arayüzü-kullanımı)
6. [Model Seçimi](#model-seçimi)
7. [Öğrenme Sistemi](#öğrenme-sistemi)
8. [Yönetici Paneli](#yönetici-paneli)
9. [Sorun Giderme](#sorun-giderme)

---

## 🖥️ Sistem Gereksinimleri

### Minimum:
- **İşletim Sistemi**: macOS, Linux, Windows (WSL2)
- **RAM**: 16GB
- **Disk**: 50GB boş alan
- **Python**: 3.9+
- **Ollama**: Yüklü ve çalışır durumda

### Önerilen (M4-Max):
- **RAM**: 128GB
- **İşlemci**: Apple M4-Max veya eşdeğeri
- **Disk**: 200GB boş alan (tüm modeller için)

---

## 🛠️ Kurulum

### 1. Projeyi İndirin
```bash
cd /Users/mikail/Desktop/NETZ-AI-Project
```

### 2. Python Bağımlılıkları
```bash
cd backend
pip install -r requirements.txt
```

### 3. Ollama Kurulumu
```bash
# macOS
brew install ollama

# Servisi başlat
ollama serve

# Modelleri indir
ollama pull mistral:latest
ollama pull llama3.2:latest
ollama pull qwen2.5-coder:32b  # Opsiyonel - 19GB
ollama pull qwen2.5:72b         # Opsiyonel - 47GB
```

### 4. Environment Variables (.env)
```env
# Backend klasöründe .env dosyası oluşturun
PENNYLANE_API_KEY=your_api_key
PENNYLANE_COMPANY_ID=22052053
GOOGLE_DRIVE_PATH=/path/to/google/drive
```

---

## 🚀 Servisleri Başlatma

### Otomatik Başlatma (Önerilen)
```bash
cd backend
python ai_training_orchestrator.py --start-services
```

### Manuel Başlatma
```bash
# Terminal 1 - Ana Chat API
python simple_api.py

# Terminal 2 - Yönetici API
python admin_api.py

# Terminal 3 - Doküman Yükleme API
python document_upload_api.py
```

### Servis Durumunu Kontrol
```bash
# Orchestrator ile
python ai_training_orchestrator.py --status

# Manuel kontrol
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
```

---

## 💬 API Kullanımı

### 1. Temel Sohbet
```bash
# Basit soru (Türkçe)
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "NETZ Informatique hangi hizmetleri sunuyor?"}
    ]
  }'

# İngilizce soru
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What services does NETZ offer?"}
    ]
  }'

# Fransızca soru
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Quels sont les services de NETZ?"}
    ]
  }'
```

### 2. Model Seçimi ile Sohbet

#### Hızlı Yanıt (Llama 3.2)
```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Merhaba nasılsın?"}
    ],
    "model_preference": "fast"
  }'
```

#### Kod Soruları (Qwen Coder)
```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Python'da async/await nasıl kullanılır?"}
    ],
    "model_preference": "coding"
  }'
```

#### Detaylı Analiz (Qwen 72B)
```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "NETZ'in 2025 finansal performansının detaylı analizi"}
    ],
    "model_preference": "accurate"
  }'
```

#### Manuel Model Seçimi
```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Excel eğitimi hakkında bilgi ver"}
    ],
    "model": "mistral:latest"
  }'
```

### 3. Model Bilgileri

#### Mevcut Modelleri Görme
```bash
curl http://localhost:8001/api/models/available
```

#### Model İstatistikleri
```bash
curl http://localhost:8001/api/models/statistics
```

#### Model Ön Yükleme
```bash
curl -X POST http://localhost:8001/api/models/preload \
  -H "Content-Type: application/json" \
  -d '["coding", "fast"]'
```

---

## 📚 Öğrenme Sistemi

### 1. Geri Bildirim Gönderme
```bash
curl -X POST http://localhost:8001/api/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session-123",
    "original_query": "Python'da async kullanımı",
    "ai_response": "Python'da async/await şöyle kullanılır...",
    "user_feedback": "Aslında async def ile fonksiyon tanımlanır, await ile asenkron fonksiyonlar beklenir. Örnek: async def main(): await asyncio.sleep(1)",
    "user_id": "user123"
  }'
```

### 2. Öğrenme Durumu
```bash
curl http://localhost:8001/api/learning-status
```

---

## 👨‍💼 Yönetici Paneli

### 1. Web Arayüzü
Tarayıcıda açın: `http://localhost:8003/admin_panel.html`

**Giriş Bilgileri:**
- Kullanıcı adı: `mikail`
- Şifre: `netz_admin_2025`

### 2. API ile Yönetim

#### Giriş Yapma
```bash
curl -X POST http://localhost:8003/admin/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "mikail",
    "password": "netz_admin_2025"
  }'
```

#### Bekleyen Katkıları Görme
```bash
curl http://localhost:8003/admin/contributions?status=pending \
  -H "X-Admin-Token: netz_admin_2025"
```

#### Katkıyı Onaylama
```bash
curl -X POST http://localhost:8003/admin/review \
  -H "Content-Type: application/json" \
  -H "X-Admin-Token: netz_admin_2025" \
  -d '{
    "contribution_id": "abc123",
    "action": "approve",
    "category": "technical",
    "approved_content": "Düzenlenmiş içerik",
    "notes": "Güzel açıklama, onaylandı"
  }'
```

---

## 📤 Doküman Yükleme

### 1. Tek Dosya Yükleme
```bash
curl -X POST http://localhost:8002/api/upload/document \
  -F "file=@/path/to/document.pdf"
```

### 2. Çoklu Dosya Yükleme
```bash
curl -X POST http://localhost:8002/api/upload/multiple \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.docx" \
  -F "files=@data.xlsx"
```

### 3. Desteklenen Formatlar
- PDF (.pdf)
- Word (.docx, .doc)
- Excel (.xlsx, .xls)
- Text (.txt)
- CSV (.csv)

---

## 🎯 Kullanım Senaryoları

### 1. Müşteri Desteği
```javascript
// Frontend'de kullanım örneği
const response = await fetch('http://localhost:8001/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    messages: [
      { role: 'user', content: 'Excel eğitimi fiyatları nedir?' }
    ],
    model_preference: 'fast'  // Hızlı yanıt için
  })
});
```

### 2. Teknik Destek
```javascript
const response = await fetch('http://localhost:8001/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    messages: [
      { role: 'user', content: 'Python'da API endpoint nasıl yazılır?' }
    ]
    // Model otomatik olarak Qwen Coder seçilecek
  })
});
```

### 3. Finansal Analiz
```javascript
const response = await fetch('http://localhost:8001/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    messages: [
      { role: 'user', content: 'Şirketimizin Q4 2025 performans analizi' }
    ],
    model_preference: 'accurate'  // Detaylı analiz için
  })
});
```

---

## 🔧 Sorun Giderme

### 1. Yavaş Yanıt Süresi
**Sorun**: Chat API 30+ saniye sürüyor

**Çözümler**:
```bash
# 1. Daha hızlı model kullan
model_preference: "fast"

# 2. Modeli önceden yükle
curl -X POST http://localhost:8001/api/models/preload \
  -d '["general", "fast"]'

# 3. RAM kontrolü
python -c "import psutil; print(f'Available RAM: {psutil.virtual_memory().available / (1024**3):.1f}GB')"
```

### 2. Model Yükleme Hatası
```bash
# Ollama servisini kontrol et
ollama list

# Modeli yeniden indir
ollama pull mistral:latest

# Ollama'yı yeniden başlat
killall ollama
ollama serve
```

### 3. API Bağlantı Hatası
```bash
# Servisleri kontrol et
ps aux | grep python | grep -E "(simple_api|admin_api|document_upload)"

# Logları kontrol et
tail -f simple_api.log
tail -f admin_api.log
```

### 4. Dil Uyumsuzluğu
**Sorun**: Türkçe soruda İngilizce yanıt

**Çözüm**: Soruya dil belirteci ekleyin:
```bash
"Türkçe olarak yanıtla: Excel eğitimi kaç saat?"
```

---

## 📊 Performans İpuçları

### 1. Optimal Model Seçimi
- **Genel sorular**: Mistral (4.4GB, 120 token/sn)
- **Kod soruları**: Qwen Coder (19GB, 40 token/sn)
- **Hızlı demo**: Llama 3.2 (2GB, 150 token/sn)
- **Detaylı analiz**: Qwen 72B (47GB, 20 token/sn)

### 2. Sistem Optimizasyonu
```bash
# GPU hızlandırma
export OLLAMA_NUM_GPU=1

# CPU thread sayısı
export OLLAMA_NUM_THREAD=20

# Model timeout
export OLLAMA_KEEP_ALIVE=5m
```

### 3. Monitoring
```python
# system_monitor.py
import psutil
import time

while True:
    print(f"CPU: {psutil.cpu_percent()}%")
    print(f"RAM: {psutil.virtual_memory().percent}%")
    print(f"Available RAM: {psutil.virtual_memory().available / (1024**3):.1f}GB")
    time.sleep(5)
```

---

## 🚨 Güvenlik Notları

1. **API Anahtarları**: .env dosyasını Git'e eklemeyin
2. **Admin Şifresi**: Production'da değiştirin
3. **CORS**: Production'da `allow_origins` kısıtlayın
4. **Rate Limiting**: Production'da ekleyin

---

## 📞 Destek

**Hata Bildirimi**: GitHub Issues
**Email**: contact@netzinformatique.fr
**Telefon**: +33 3 67 31 02 01

---

*Son güncelleme: 2025-01-10*