# NETZ AI Belge Yükleme ve Eğitim Kılavuzu

## 🚀 Hızlı Başlangıç

### 1. Sistemi Başlatma
```bash
# Backend servisleri başlat
cd backend
python simple_api.py &         # Ana AI servisi (port 8001)
python document_upload_api.py & # Belge yükleme servisi (port 8002)

# Frontend'i başlat
cd ../frontend
npm run dev                     # Web arayüzü (port 3000)
```

### 2. Web Arayüzünden Belge Yükleme

1. Tarayıcıda `http://localhost:3000` adresine gidin
2. Sol menüden **"Ajouter Documents"** (Belge Ekle) butonuna tıklayın
3. Açılan sayfada:
   - Dosyaları sürükle-bırak ile yükleyin
   - veya "dosya seç" linkine tıklayarak seçin
4. Desteklenen formatlar:
   - PDF dosyaları
   - Word belgeleri (.docx, .doc)
   - Excel dosyaları (.xlsx, .xls)
   - Metin dosyaları (.txt, .csv)

### 3. Yüklenen Belgeler

Yüklediğiniz belgeler:
- Otomatik olarak işlenir ve AI hafızasına eklenir
- Tekrar eden belgeler otomatik olarak tespit edilir
- Her belge için özet önizleme gösterilir
- İstenmeyen belgeler silinebilir

## 📊 Mevcut Veriler

AI şu anda şu bilgilere sahip:

### Finansal Veriler
- **2025 Ocak-Ekim Gelir**: 119,386.85€
- **Ekim 2025**: 41,558.85€ (en yüksek ay)
- **Yıllık Projeksiyon**: 143,264.22€

### Eğitim Gelirleri
1. **Excel**: 35,815.85€ (30%)
2. **Bilan de compétences**: 28,500€ (23.9%)
3. **Python**: 19,000€ (15.9%)
4. **AutoCAD**: 13,058.85€ (10.9%)
5. **WordPress**: 11,264€ (9.4%)

### Şirket Bilgileri
- **SIRET**: 818 347 346 00020
- **Adres**: 1A Route de Schweighouse, 67500 HAGUENAU
- **Müdür**: Mikail LEKESIZ
- **Müşteri Sayısı**: 2,734

## 🔧 Gelişmiş Kullanım

### API ile Belge Yükleme
```bash
# Tek dosya yükleme
curl -X POST http://localhost:8002/api/upload/document \
  -F "file=@/path/to/document.pdf"

# Yüklenen belgeleri listeleme
curl http://localhost:8002/api/documents/list

# Belge silme
curl -X DELETE http://localhost:8002/api/documents/{file_hash}
```

### AI'ya Soru Sorma
```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Ekim ayı ciromuz nedir?"}]}'
```

## 📁 Önerilen Belge Türleri

### Finansal Belgeler
- Aylık gelir raporları
- Fatura örnekleri
- Muhasebe raporları
- Banka ekstreleri

### Eğitim Belgeleri
- Eğitim programları
- Sertifika örnekleri
- Müfredat detayları
- Başarı oranları

### Müşteri Belgeleri
- Müşteri listeleri
- Referans mektupları
- Başarı hikayeleri
- Geri bildirimler

### Yasal Belgeler
- Sözleşme şablonları
- RGPD politikaları
- Kullanım koşulları
- Gizlilik politikaları

## ⚠️ Güvenlik Uyarıları

1. **Hassas Bilgiler**
   - Kişisel bilgileri (TC No, telefon) yüklemeden önce silin
   - Banka hesap numaralarını karartın
   - Şifreleri asla yüklemeyin

2. **Veri Gizliliği**
   - Tüm veriler yerel sunucuda saklanır
   - Dışarıya veri gönderilmez
   - Düzenli yedekleme yapın

## 🆘 Sorun Giderme

### API Çalışmıyor
```bash
# Servisleri kontrol et
ps aux | grep python

# Logları kontrol et
tail -f simple_api.log
tail -f document_upload.log
```

### Belge Yüklenemiyor
- Dosya boyutu 10MB'dan küçük mü?
- Dosya formatı destekleniyor mu?
- API servisi çalışıyor mu?

### AI Yanlış Cevap Veriyor
- İlgili belgeleri yüklediniz mi?
- Belgeler güncel mi?
- Çelişen bilgiler var mı?

## 📞 Destek

Sorunlar için:
- Email: mikail@netzinformatique.fr
- Log dosyaları: `/backend/*.log`
- Sistem durumu: `http://localhost:8002/health`

---

*Son güncelleme: 9 Ocak 2025*