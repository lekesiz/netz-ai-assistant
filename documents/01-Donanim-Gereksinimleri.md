# NETZ Informatique Offline AI - Donanım Gereksinimleri Raporu

## 🖥️ Özet
Bu rapor, NETZ Informatique için kurulacak offline AI sisteminin donanım gereksinimlerini detaylandırmaktadır.

## 📊 Sistem Konfigürasyonları

### 1. Minimum Konfigürasyon (5-10 Kullanıcı)
- **İşlemci**: Intel i7-13700K veya AMD Ryzen 7 7700X (16 çekirdek)
- **RAM**: 64 GB DDR5 (4800MHz)
- **GPU**: NVIDIA RTX 4070 Ti (12GB VRAM) veya RTX A4000 (16GB)
- **Depolama**: 
  - 1TB NVMe SSD (Sistem ve model)
  - 4TB HDD (Veri depolama)
- **PSU**: 850W 80+ Gold
- **Soğutma**: Liquid cooling sistem
- **Tahmini Maliyet**: €3,500 - €4,500

### 2. Önerilen Konfigürasyon (20-50 Kullanıcı)
- **İşlemci**: Intel Xeon W-2445 veya AMD Threadripper PRO 5955WX
- **RAM**: 128 GB DDR5 ECC (Hata düzeltmeli)
- **GPU**: NVIDIA RTX 4090 (24GB) veya RTX A5000 (24GB)
- **Depolama**:
  - 2TB NVMe SSD (RAID 1)
  - 8TB Enterprise HDD (RAID 5)
- **PSU**: 1200W 80+ Platinum Redundant
- **Şasi**: Rack-mount 4U server şasi
- **Tahmini Maliyet**: €8,000 - €12,000

### 3. Enterprise Konfigürasyon (50+ Kullanıcı)
- **Sunucu**: Dell PowerEdge R750 veya HPE ProLiant DL380 Gen11
- **İşlemci**: 2x Intel Xeon Gold 6338 (32 çekirdek/64 thread toplam)
- **RAM**: 256 GB DDR4 ECC
- **GPU**: 2x NVIDIA A100 (40GB) veya 4x RTX 4090
- **Depolama**:
  - 4TB NVMe SSD (RAID 10)
  - 20TB Enterprise SAS HDD (RAID 6)
- **Network**: 10Gb Ethernet
- **Yedekleme**: UPS (3000VA minimum)
- **Tahmini Maliyet**: €25,000 - €40,000

## 🔧 Kritik Bileşen Detayları

### GPU Seçimi
- **Inference için**: RTX 4070 Ti veya üzeri
- **Fine-tuning için**: Minimum 24GB VRAM (RTX 4090/A5000)
- **Multi-user için**: Çoklu GPU desteği gerekli

### RAM Gereksinimleri
- Model yükleme: ~16GB
- Context window: ~32GB (8K token)
- Multi-threading: Kullanıcı başı ~4GB
- İşletim sistemi: ~8GB

### Depolama Hesaplaması
- Base model: ~50GB
- Fine-tuned model: ~100GB
- Vector database: ~500GB (başlangıç)
- Doküman arşivi: ~1TB
- Log ve backup: ~2TB

## 📈 Ölçeklendirme Planı

### Faz 1 (0-6 ay)
- Minimum konfigürasyon ile başlangıç
- 5-10 kullanıcı desteği
- Temel model deployment

### Faz 2 (6-12 ay)
- GPU upgrade (24GB VRAM)
- RAM artırımı (128GB)
- Vector database optimizasyonu

### Faz 3 (12+ ay)
- Enterprise konfigürasyona geçiş
- Multi-GPU setup
- High availability kurulumu

## 🛡️ Güvenlik Donanımları

1. **Hardware Security Module (HSM)**
   - Yubico YubiHSM 2
   - Şifreleme anahtarı yönetimi

2. **Network Security**
   - Dedicated firewall appliance
   - Air-gapped network seçeneği

3. **Fiziksel Güvenlik**
   - Kilitli server kabini
   - Biometric erişim kontrolü

## 💡 Öneriler

1. **Başlangıç için**: Önerilen konfigürasyon ideal
2. **GPU önceliği**: VRAM > CUDA cores
3. **Yedekleme**: RAID + External backup zorunlu
4. **Monitoring**: IPMI/iDRAC uzaktan yönetim
5. **Gelecek garantisi**: PCIe 5.0 ve DDR5 desteği

## 📋 Satın Alma Kontrol Listesi

- [ ] Server/Workstation seçimi
- [ ] GPU compatibility kontrolü
- [ ] ECC RAM gerekliliği değerlendirmesi
- [ ] Cooling kapasitesi hesaplaması
- [ ] UPS sizing (VA hesabı)
- [ ] Network infrastructure hazırlığı
- [ ] Backup storage planlaması
- [ ] Warranty ve support paketleri

---
*Son güncelleme: 2025-01-09*