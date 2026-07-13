# Shopee Flashsale BOT

Selenium-based bot untuk auto-beli di flash sale Shopee Indonesia.

> ⚠️ **Disclaimer:** Project ini untuk **tujuan edukasi**. Shopee melarang penggunaan bot untuk pembelian. Penggunaan dapat menyebabkan akun Anda di-suspend/di-block oleh Shopee. Gunakan dengan risiko Anda sendiri.

## Author

**YOS** — [@yosyoss](https://github.com/yosyoss)

---

## Requirements

- Python 3.8+
- Google Chrome (versi apapun)
- Koneksi internet

## Installation

```bash
# 1. Clone repository
git clone https://github.com/yosyoss/Shopee-Flashsale-BOT.git
cd Shopee-Flashsale-BOT

# 2. Install dependencies
pip install -r requirements.txt
```

## Setup Chrome (Penting!)

Project ini pakai **Chrome for Testing** portable + CDP attach. Langkahnya:

```bash
# 1. Download Chrome for Testing (sudah ada di folder chrome-portable/ jika Anda clone)
#    Atau download manual dari:
#    https://googlechromelabs.github.io/chrome-for-testing/

# 2. Login Shopee SEKALI di Chrome portable
double-click open_portable_chrome.bat
# → Chrome portable terbuka
# → Login Shopee, close Chrome
# → Cookies tersimpan di ./chrome-profile/
```

## Usage

```bash
# 1. Edit config/index.json - masukkan URL flash sale
#    "url": "https://shopee.co.id/..."

# 2. Jalankan bot
py main.py
# atau
python main.py

# 3. Di menu, pilih 1. START COUNTDOWN
```

## Alur Bot

1. **Bot buka Chrome** portable (visible) — user bisa lihat
2. **Bot navigasi ke homepage** Shopee (anti-bot friendly)
3. **User navigasi MANUAL** ke URL flash sale (paste di address bar)
4. **Bot deteksi login** (cookies + URL `is_logged_in=true`)
5. **User pilih varian** (warna/ukuran) di Chrome
6. **Bot polling flash sale** — deteksi otomatis atau tekan Enter untuk GO NOW
7. **Bot auto-klik:** Beli Sekarang → Checkout → Buat Pesanan

## Catatan Penting

- **Jangan auto-navigate** ke product URL dari bot (trigger Shopee captcha)
- User HARUS navigate manual di Chrome untuk hindari captcha
- Pilih varian SEBELUM flash sale timer habis
- Tekan **Enter** di terminal kapan saja untuk force-click Buy
- Shopee mungkin block checkout terakhir dengan M01 popup — itu normal, click OK + Buat Pesanan manual

## Struktur Project

```
Shopee-Flashsale-BOT/
├── main.py                          # Entry point
├── config/
│   └── index.json                   # URL & config
├── lib/
│   ├── moduleChecker.py             # Check & install dependencies
│   ├── definitions.py               # Menu & config UI
│   └── driverExecutor.py            # Core bot logic
├── chrome-portable/                 # Chrome for Testing (download manual)
├── chrome-profile/                  # Shopee cookies (auto-created)
├── webdriver/
│   └── chromedriver.exe             # ChromeDriver (v150)
├── open_portable_chrome.bat         # Script untuk login Shopee
├── requirements.txt                 # Python deps
└── README.md
```

## Troubleshooting

**Q: Chrome tidak bisa start**
Pastikan Python 3.8+ dan dependencies terinstall: `pip install -r requirements.txt`

**Q: Captcha muncul terus**
Pastikan navigasi ke product URL dilakukan MANUAL (paste di address bar), bukan via bot

**Q: Bot tidak detect product page**
Tunggu beberapa detik, atau tekan Enter di terminal untuk skip manual

**Q: M01 popup "suspicious activity"**
Normal. Click OK lalu klik "Buat Pesanan" manual di Chrome.

## License

MIT License - bebas digunakan, dimodifikasi, dan didistribusikan.
