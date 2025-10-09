# NETZ AI Eğitim Rehberi

## 🎯 AI Modelinizi Optimize Etmek İçin Yapabilecekleriniz

### 1. **VERİ KAYNAKLARI**

#### A. Google Drive Belgeleri
- **Finansal Belgeler**: URSSAF, banka ekstreleri, faturalar
- **Eğitim Materyalleri**: Formation-Haguenau-Ai.pdf gibi
- **Şirket Belgeleri**: Organizasyon yapısı, sözleşmeler
- **Müşteri Belgeleri**: Faturalar, sözleşmeler

#### B. PennyLane Muhasebe Verileri
- Güncel gelir/gider raporları
- Müşteri faturaları
- KDV beyannameleri
- Mali tablolar

#### C. Gmail Verileri
- Müşteri yazışmaları
- Teklif ve sözleşmeler
- Destek talepleri
- Randevu kayıtları

### 2. **VERİ HAZIRLAMA**

#### Yapılması Gerekenler:

1. **Belgeleri Kategorilere Ayırın**:
   ```
   /Finansal
   /Eğitimler
   /Müşteriler
   /Yasal
   /Pazarlama
   ```

2. **Hassas Verileri Temizleyin**:
   - Kişisel bilgiler (TC No, telefon)
   - Banka hesap numaraları
   - Şifreler

3. **Metadata Ekleyin**:
   - Belge türü
   - Tarih
   - İlgili departman
   - Öncelik seviyesi

### 3. **EĞİTİM SÜRECİ**

#### A. Otomatik Veri Yükleme
```bash
# Tüm belgeleri yükle
python load_all_documents.py

# Sadece önemli belgeleri yükle
python load_priority_docs.py
```

#### B. Soru-Cevap Çiftleri Oluşturun
```json
{
  "questions": [
    {
      "q": "2025 yılı toplam ciromuz nedir?",
      "a": "2025 yılı Ocak-Ekim arası toplam ciromuz 119,386.85€'dur."
    },
    {
      "q": "En çok talep gören eğitimimiz hangisi?",
      "a": "Excel eğitimi, toplam ciromuzun %30'unu oluşturarak en çok talep gören eğitimimizdir."
    }
  ]
}
```

#### C. Özel Durumlar İçin Eğitim
- Teknik destek senaryoları
- Satış süreçleri
- Müşteri şikayetleri
- Yasal konular

### 4. **TEST VE İYİLEŞTİRME**

#### A. Test Soruları Hazırlayın:
1. Finansal sorular
2. Eğitim içerik soruları
3. Müşteri bilgi sorguları
4. Teknik destek soruları

#### B. Performans Metrikleri:
- Doğruluk oranı
- Cevap süresi
- Kaynak kullanımı
- Müşteri memnuniyeti

### 5. **SÜREKLİ İYİLEŞTİRME**

#### Haftalık Görevler:
- [ ] Yeni belgeleri yükle
- [ ] Yanlış cevapları düzelt
- [ ] Eksik bilgileri tamamla
- [ ] Performans raporu oluştur

#### Aylık Görevler:
- [ ] Model performans analizi
- [ ] Müşteri geri bildirimlerini değerlendir
- [ ] Yeni özellikler ekle
- [ ] Güvenlik güncellemeleri

### 6. **GÜVENLİK VE GİZLİLİK**

#### Dikkat Edilmesi Gerekenler:
1. **RGPD Uyumluluğu**
   - Kişisel verileri anonimleştir
   - Veri saklama sürelerine uy
   - Erişim logları tut

2. **Veri Güvenliği**
   - Şifreleme kullan
   - Yedekleme yap
   - Erişim kontrolü uygula

3. **Etik Kurallar**
   - Yanıltıcı bilgi verme
   - Müşteri sırlarını koru
   - Profesyonel dil kullan

### 7. **HIZLI BAŞLANGIÇ**

```bash
# 1. Mevcut durumu kontrol et
python check_ai_status.py

# 2. Eksik verileri yükle
python sync_all_data.py

# 3. Test et
python test_ai_responses.py

# 4. Canlıya al
python deploy_ai.py
```

### 8. **EN İYİ UYGULAMALAR**

1. **Veri Kalitesi**
   - Güncel tut
   - Doğrula
   - Tutarlı format kullan

2. **Model Eğitimi**
   - Küçük güncellemeler yap
   - Test ortamında dene
   - Geri dönüş planı hazırla

3. **İzleme**
   - Log analizi
   - Hata takibi
   - Performans metrikleri

### 9. **DESTEK**

Sorularınız için:
- Email: mikail@netzinformatique.fr
- Dokümantasyon: /docs klasörü
- Log dosyaları: /logs klasörü

---

*Son güncelleme: 9 Ocak 2025*