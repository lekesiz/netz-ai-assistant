# 🚀 NETZ AI Hızlı Test Kılavuzu

## 📍 Mevcut Durum
- ✅ Backend API çalışıyor: http://localhost:8001
- ✅ Frontend çalışıyor: http://localhost:3000
- ✅ Dil algılama sistemi aktif
- ⏳ RAG sistemi için Docker gerekli

## 🧪 Hemen Test Edebilirsiniz

### 1. Web Arayüzünden Test
Tarayıcınızda: **http://localhost:3000/chat**

### 2. Terminal'den Test

#### Türkçe Test:
```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "NETZ hangi hizmetleri sunuyor?"}]}'
```

#### Fransızca Test:
```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Quels sont vos services de formation?"}]}'
```

#### İngilizce Test:
```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "What training programs do you offer?"}]}'
```

## 📊 Beklenen Sonuçlar

1. **Yanıt Dili**: Soru hangi dildeyse yanıt da o dilde olmalı
2. **Yanıt Süresi**: 10-20 saniye arası
3. **İçerik**: NETZ'in gerçek verileri (fiyatlar, hizmetler, vs.)

## 🔍 Kontrol Edilecekler

- ✓ Dil uyumu doğru mu?
- ✓ Bilgiler güncel mi? (2025 verileri)
- ✓ Fiyatlar doğru mu?
- ✓ Hizmet listesi tam mı?

## 💡 İpuçları

1. İlk sorgu biraz uzun sürebilir (model yükleniyor)
2. Sonraki sorgular daha hızlı olacaktır
3. Her dilde en az 2-3 soru deneyin

## 🎯 Örnek Test Senaryoları

### Senaryo 1: Fiyat Bilgisi
- TR: "Excel eğitimi ne kadar?"
- FR: "Combien coûte la formation Excel?"
- EN: "How much does Excel training cost?"

**Beklenen**: 690€ - 1,500€ HT (21-35 saat)

### Senaryo 2: Müşteri Sayısı
- TR: "Kaç aktif müşteriniz var?"
- FR: "Combien de clients actifs avez-vous?"
- EN: "How many active clients do you have?"

**Beklenen**: 2,734 aktif müşteri

### Senaryo 3: Başarı Oranı
- TR: "Sertifika başarı oranınız nedir?"
- FR: "Quel est votre taux de réussite?"
- EN: "What is your certification success rate?"

**Beklenen**: %87 başarı oranı

---

*Test ederken herhangi bir sorun yaşarsanız, lütfen hata mesajlarını paylaşın.*