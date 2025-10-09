# GitHub'a Yükleme Talimatları

## 1. GitHub'da Repository Oluştur

GitHub.com'da yeni bir repository oluşturun:
- Repository adı: `netz-ai-assistant` (veya istediğiniz isim)
- Description: "NETZ Informatique Offline AI Assistant - Enterprise-grade offline AI system"
- Public/Private: İstediğiniz gibi (önerim: Private)
- **ÖNEMLİ**: "Initialize this repository with a README" seçeneğini **işaretlemeyin**

## 2. Remote Repository Ekle

Terminal'de proje klasöründeyken:

```bash
# GitHub repository URL'nizi ekleyin
git remote add origin https://github.com/KULLANICI_ADINIZ/REPO_ADINIZ.git

# Örnek:
# git remote add origin https://github.com/netzinformatique/netz-ai-assistant.git
```

## 3. İlk Push

```bash
# Main branch'e push edin
git push -u origin main
```

## 4. GitHub Personal Access Token (Eğer Gerekirse)

Eğer şifre sorulursa ve 2FA aktifse:
1. GitHub → Settings → Developer settings → Personal access tokens
2. "Generate new token (classic)" tıklayın
3. Expiration: 90 days (veya istediğiniz)
4. Scopes: `repo` (tüm repo yetkileri)
5. Token'ı kopyalayın ve şifre yerine kullanın

## 5. Alternatif: SSH Kullanımı

SSH key kullanmak isterseniz:

```bash
# SSH key oluştur (yoksa)
ssh-keygen -t ed25519 -C "email@example.com"

# Public key'i kopyala
cat ~/.ssh/id_ed25519.pub

# GitHub'a ekle: Settings → SSH and GPG keys → New SSH key

# Remote URL'yi SSH olarak değiştir
git remote set-url origin git@github.com:KULLANICI_ADINIZ/REPO_ADINIZ.git

# Push
git push -u origin main
```

## 6. Repository Ayarları

GitHub'da repository'ye gittikten sonra:

### Settings → General
- Features: Issues ✓, Wiki ✓, Projects ✓

### Settings → Branches
- Default branch: main
- Branch protection rules ekleyin (opsiyonel)

### Settings → Security
- Dependabot alerts: Enable
- Secret scanning: Enable

## 7. README Güncelleme

GitHub'da görünecek şekilde README'ye eklemeler:

```markdown
## 🚀 Demo
[Demo URL veya screenshot]

## 📊 Status
![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)

## 🤝 Contributors
- [İsminiz](https://github.com/username)
```

## 8. Güvenlik Notları

⚠️ **DİKKAT**: Push etmeden önce kontrol edin:
- `.env` dosyası `.gitignore`'da mı?
- API anahtarları, şifreler kod içinde yok mu?
- Hassas müşteri verileri yok mu?

## 9. Sonraki Commitler

```bash
# Değişiklikleri ekle
git add .

# Commit oluştur
git commit -m "Açıklayıcı commit mesajı"

# Push et
git push
```

## 10. GitHub Actions (Opsiyonel)

CI/CD için `.github/workflows/ci.yml` ekleyebilirsiniz:

```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          echo "Tests would run here"
```

---

✅ **Hazırsınız!** Yukarıdaki adımları takip ederek projeyi GitHub'a yükleyebilirsiniz.