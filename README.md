# NETZ Informatique AI System

## 🚀 Özet
NETZ Informatique için tamamen offline çalışan, şirket özel bilgilerine sahip kurumsal AI asistanı.

## 📋 Özellikler
- ✅ Tamamen offline çalışma (air-gapped deployment)
- ✅ Fransızca optimize edilmiş AI modeller
- ✅ Google Workspace entegrasyonu (Drive, Gmail, Calendar)
- ✅ Güvenli multi-user erişim kontrolü
- ✅ Otomatik veri güncelleme ve model eğitimi
- ✅ Enterprise-grade güvenlik ve monitoring

## 🏗️ Sistem Mimarisi

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Client    │────▶│  Kong Gateway   │────▶│   FastAPI       │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                          │
                        ┌─────────────────────────────────┴────────┐
                        │                                          │
                  ┌─────┴─────┐  ┌──────────────┐  ┌─────────────┴───┐
                  │   vLLM    │  │    Qdrant    │  │   PostgreSQL    │
                  │  Server   │  │  Vector DB   │  │    Database     │
                  └───────────┘  └──────────────┘  └─────────────────┘
```

## 📦 Proje Yapısı

```
NETZ-AI-Project/
├── documents/          # Detaylı dokümantasyon
│   ├── 01-Donanim-Gereksinimleri.md
│   ├── 02-Yazilim-Stack-Teknoloji-Secimi.md
│   ├── 03-LLM-Model-Secimi-Kurulum.md
│   ├── 04-Veri-Toplama-Egitim-Plani.md
│   └── 05-Guvenlik-Erisim-Kontrolu.md
├── scripts/           # Kurulum ve yönetim scriptleri
│   ├── install.sh     # Ana kurulum scripti
│   └── backup.sh      # Yedekleme scripti
├── configs/           # Konfigürasyon dosyaları
│   ├── docker-compose.yml
│   └── .env.template
├── services/          # Systemd service dosyaları
│   ├── netz-llm.service
│   └── netz-api.service
├── data/             # Veri dizinleri (boş)
├── models/           # Model dizinleri (boş)
└── training/         # Eğitim scriptleri (gelecek)
```

## 🚀 Hızlı Başlangıç

### 1. Sistem Gereksinimleri
- Ubuntu Server 22.04 LTS
- Minimum 64GB RAM
- NVIDIA GPU (RTX 4070 Ti veya üzeri)
- 2TB+ depolama alanı

### 2. Kurulum

```bash
# Repository'yi klonla
git clone https://github.com/netz-informatique/netz-ai.git
cd netz-ai

# Kurulum scriptini çalıştır
sudo bash scripts/install.sh
```

### 3. Konfigürasyon

```bash
# Environment dosyasını oluştur
cp configs/.env.template /etc/netz-ai/.env

# Değerleri düzenle
sudo nano /etc/netz-ai/.env
```

### 4. Servisleri Başlat

```bash
# Tüm servisleri başlat
sudo systemctl start netz-llm
sudo systemctl start netz-api
sudo systemctl start netz-worker

# Durumu kontrol et
sudo systemctl status netz-*
```

## 🔐 İlk Giriş

1. Web arayüzüne gidin: `https://netz-ai.local`
2. Admin kullanıcısı ile giriş yapın
3. Şifreleri değiştirin
4. Kullanıcıları ve rolleri yapılandırın

## 📊 Monitoring

- Grafana: `http://localhost:3001` (admin/CHANGE_ME)
- Prometheus: `http://localhost:9090`
- Keycloak: `http://localhost:8080` (admin/CHANGE_ME)

## 🔧 Yönetim Komutları

```bash
# Backup al
sudo /opt/netz-ai/scripts/backup.sh

# Logları görüntüle
sudo journalctl -u netz-api -f

# Model güncelle
sudo -u netz-ai /opt/netz-ai/scripts/update-model.sh

# Sistem durumu
sudo /opt/netz-ai/scripts/health-check.sh
```

## 📚 Detaylı Dokümantasyon

Her konu için detaylı dokümantasyon `documents/` klasöründe bulunmaktadır:

1. **Donanım Gereksinimleri**: Minimum, önerilen ve enterprise konfigürasyonlar
2. **Yazılım Stack**: Kullanılan teknolojiler ve mimarisi
3. **Model Seçimi**: LLM modelleri ve kurulum detayları
4. **Veri Toplama**: Google Workspace entegrasyonu ve eğitim süreci
5. **Güvenlik**: Erişim kontrolü, şifreleme ve güvenlik politikaları

## 🛡️ Güvenlik Notları

- Tüm default şifreleri değiştirin
- Firewall kurallarını kontrol edin
- SSL sertifikalarını production için güncelleyin
- Düzenli backup alın
- Audit loglarını monitör edin

## 🆘 Sorun Giderme

### GPU Tanınmıyor
```bash
nvidia-smi
# CUDA driver kurulumu gerekebilir
```

### Model Yükleme Hatası
```bash
# Model dosyalarını kontrol et
ls -la /opt/netz-ai/models/
```

### API Bağlantı Hatası
```bash
# Service durumunu kontrol et
sudo systemctl status netz-api
# Logları incele
sudo journalctl -u netz-api -n 100
```

## 📧 İletişim

NETZ Informatique  
Email: support@netz-informatique.fr  
Tel: +33 X XX XX XX XX

## 📄 Lisans

Bu proje NETZ Informatique'e özeldir ve gizlilik sözleşmesi kapsamındadır.

---
*Son güncelleme: 2025-01-09*