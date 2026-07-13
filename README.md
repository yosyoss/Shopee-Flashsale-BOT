# 🛒 Shopee Flashsale BOT

> **Bot otomatis untuk beli flash sale Shopee Indonesia** — built with Python + Selenium + Chrome DevTools Protocol.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Selenium-4-green?logo=selenium&logoColor=white)](https://selenium-python.readthedocs.io/)
[![Chrome](https://img.shields.io/badge/Chrome_for_Testing-v150-4285F4?logo=google-chrome&logoColor=white)](https://googlechromelabs.github.io/chrome-for-testing/)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?logo=windows)](https://www.microsoft.com/windows)

Bot Selenium yang membuka Chrome **portable**, login Shopee dari cookies yang tersimpan, dan otomatis klik **Beli → Checkout → Buat Pesanan** saat flash sale aktif. Dilengkapi **manual GO trigger** (tekan Enter di terminal) untuk akurasi milidetik.

---

## ⚠️ Disclaimer

> Project ini untuk **tujuan edukasi dan riset**. Penggunaan bot untuk pembelian melanggar Terms of Service Shopee. Akun Anda bisa di-suspend, di-block, atau di-ban永久. **Gunakan dengan risiko Anda sendiri.**

---

## 🎯 Fitur

| Fitur | Deskripsi |
|-------|-----------|
| 🪟 **Visible browser** | Chrome portable dibuka visible, Anda bisa lihat & interaksi |
| 🔐 **Auto login** | Login Shopee sekali via cookies, persist di profile |
| 🛒 **Auto Beli** | Otomatis klik "Beli Sekarang" saat flash sale aktif |
| 💳 **Auto Checkout** | Otomatis klik Checkout → Buat Pesanan |
| ⚡ **Manual GO trigger** | Tekan Enter di terminal untuk force-click (akurasi milidetik) |
| 🔀 **Multi-selector fallback** | Shopee markup changes? Bot try 5+ selector sampai ketemu |
| ⏱️ **Time-based detection** | Detect "berakhir dalam" / "dimulai dalam" / "stok tersisa" |
| 🛡️ **Anti-captcha** | User navigasi manual ke product URL, hindari Shopee captcha |

---

## 📦 Requirements

- **Python 3.8+** ([download](https://www.python.org/downloads/))
- **Google Chrome for Testing portable** (auto-included via download, atau manual)
- **Koneksi internet** stabil
- **Akun Shopee** yang sudah login

---

## 🚀 Instalasi

### Step 1: Clone repository

```bash
git clone https://github.com/yosyoss/Shopee-Flashsale-BOT.git
cd Shopee-Flashsale-BOT
```

### Step 2: Install Python dependencies

```bash
pip install -r requirements.txt
```

Atau pakai `py -m pip` kalau `pip` tidak ada:
```bash
py -m pip install -r requirements.txt
```

### Step 3: Download Chrome for Testing portable

Project ini butuh **Chrome for Testing v150** (portable, ~420MB). Ada 2 cara:

#### Opsi A: Download manual (recommended)

1. Buka https://googlechromelabs.github.io/chrome-for-testing/
2. Pilih versi **Stable 150.0.7871.115** (atau lebih baru)
3. Download **chrome-win64.zip** untuk Windows
4. Extract ke folder `chrome-portable/chrome-win64/` di project ini
5. Pastikan struktur folder jadi:
   ```
   chrome-portable/
   └── chrome-win64/
       ├── chrome.exe
       ├── chrome.dll
       └── ... (file lain)
   ```

#### Opsi B: Pakai Chrome yang sudah ada di repo

Project ini **sudah include** Chrome portable di `chrome-portable/` (kalau Anda clone fresh). Cek:
```bash
ls chrome-portable/chrome-win64/chrome.exe
```
Kalau ada, langsung lanjut ke Step 4.

### Step 4: Download ChromeDriver

ChromeDriver harus match versi Chrome (v150). Project ini sudah include di `webdriver/chromedriver.exe`. Cek:
```bash
ls webdriver/chromedriver.exe
```

Kalau belum ada, download manual:
1. Buka https://googlechromelabs.github.io/chrome-for-testing/
2. Pilih versi yang sama dengan Chrome (150.0.7871.115)
3. Download **chromedriver-win64.zip**
4. Extract `chromedriver.exe` ke folder `webdriver/`

---

## 🔐 Setup Login Shopee (SEKALI SAJA!)

Bot perlu cookies Shopee dari akun Anda. Login **sekali** di Chrome portable, cookies akan tersimpan permanen.

### Step A: Buka Chrome portable via script

**Double-click** `open_portable_chrome.bat` di File Explorer.

Atau via PowerShell:
```powershell
cd C:\path\to\Shopee-Flashsale-BOT
.\open_portable_chrome.bat
```

### Step B: Login Shopee

1. Chrome portable terbuka ke `https://shopee.co.id`
2. Klik tombol **"Login"** di kanan atas
3. Masukkan **email/nomor HP + password** akun Shopee Anda
4. Selesaikan **captcha** kalau diminta
5. Pastikan Anda **fully logged in** (terlihat username/avatar di kanan atas)

### Step C: Close Chrome

Tutup Chrome (klik X atau Ctrl+W).

> ✅ **Cookies Shopee tersimpan** di `chrome-profile/`. Anda tidak perlu login lagi di kemudian hari — kecuali cookies expired.

---

## 🎮 Cara Pakai

### Step 1: Edit URL target

Buka `config/index.json` dan set URL flash sale yang dituju:
```json
{
    "url": "https://shopee.co.id/PRODUCT-NAME-i.SHOPID.ITEMID",
    ...
}
```

### Step 2: Jalankan bot

```bash
py main.py
```

Atau klik 2x `main.py` di File Explorer.

### Step 3: Pilih menu

Di terminal, pilih **`1. START COUNTDOWN`**:
```
[?] Welcome to Shopee Flash Sale Bot, Select one menu..:
 > 1. START COUNTDOWN
   2. OPTIONS
   3. RESET
   4. EXIT
```

### Step 4: Di Chrome yang terbuka

1. Chrome portable terbuka ke **Shopee homepage** (logged in otomatis)
2. **Navigasi MANUAL** ke URL flash sale (paste di address bar)
   - ⚠️ **JANGAN** minta bot navigate otomatis (trigger Shopee captcha)
3. Pilih **varian** (warna/ukuran) di Chrome
4. Tunggu timer flash sale Shopee di Chrome

### Step 5: Trigger Buy

**Opsi A — Otomatis:** Bot deteksi timer Shopee, auto-click
**Opsi B — Manual:** Tekan **Enter** di terminal kapan saja untuk force-click Buy

### Step 6: Selesai

Bot otomatis:
1. ✅ Klik **"Beli Sekarang"**
2. ✅ Check item di cart
3. ✅ Klik **"Checkout"**
4. ✅ Klik **"Buat Pesanan"**

Kalau Shopee tampilkan popup **M01 (suspicious activity)** — itu normal. Click **OK** lalu click **"Buat Pesanan"** manual.

---

## 📂 Struktur Project

```
Shopee-Flashsale-BOT/
├── 📄 main.py                      # Entry point
├── 📄 requirements.txt             # Python dependencies
├── 📄 README.md                    # This file
├── 📄 .gitignore
│
├── 📁 config/
│   └── index.json                  # URL & setting configuration
│
├── 📁 lib/
│   ├── moduleChecker.py            # Auto-install dependencies
│   ├── definitions.py              # Menu & config UI
│   └── driverExecutor.py           # Core bot logic
│
├── 📁 chrome-portable/             # Chrome for Testing (download manual)
│   └── chrome-win64/
│       └── chrome.exe              # ~420MB
│
├── 📁 chrome-profile/              # Shopee cookies (auto-created, JANGAN share!)
│   └── Default/                    # Profile dengan login Shopee
│
├── 📁 webdriver/
│   └── chromedriver.exe            # ChromeDriver v150
│
├── 🛠️ open_portable_chrome.bat    # Buka Chrome portable untuk login Shopee
├── 🛠️ launch_chrome_debug.bat     # Launcher alternatif
├── 🛠️ launch_chrome_debug.ps1
└── 🛠️ push_to_new_repo.ps1        # Helper untuk push ke GitHub
```

---

## 🔧 Troubleshooting

### ❌ "Chrome tidak bisa start"

Pastikan:
- ✅ Python 3.8+ terinstall: `python --version`
- ✅ Dependencies terinstall: `pip install -r requirements.txt`
- ✅ File `chrome-portable/chrome-win64/chrome.exe` ada
- ✅ File `webdriver/chromedriver.exe` ada
- ✅ Versi Chrome match dengan chromedriver (keduanya v150)

### ❌ "Captcha Shopee muncul terus"

**JANGAN** minta bot navigate otomatis ke product URL. Solusi:
1. Bot buka Chrome ke **homepage**
2. **Anda** yang navigate manual ke product URL (paste di address bar)
3. Shopee tidak detect ini sebagai bot

### ❌ "Bot tidak detect product page"

Tunggu 5-10 detik setelah navigate manual. Atau tekan **Enter** di terminal untuk skip manual.

### ❌ "M01 popup - Checkout gagal karena aktivitas mencurigakan"

**Normal!** Shopee verifikasi "apakah ini manusia?" di step terakhir.

**Solusi:**
1. Click **OK** di popup
2. Click **"Buat Pesanan"** (oranye) **manual** di Chrome
3. Order masuk ✅

### ❌ "Login Shopee ter-reset / tidak detected"

Cookies expired. Ulangi:
1. Double-click `open_portable_chrome.bat`
2. Login Shopee manual
3. Close Chrome
4. Run `py main.py` lagi

### ❌ Masih ada masalah?

Buka [GitHub Issues](https://github.com/yosyoss/Shopee-Flashsale-BOT/issues) — sertakan:
- Output error message
- Screenshot
- Versi Python (`python --version`)
- Versi Chrome di `chrome-portable/`

---

## ⚙️ Konfigurasi Lanjutan

Edit `config/index.json`:
```json
{
    "session": "mysession.json",         // File session (legacy, opsional)
    "url": "https://shopee.co.id/...",   // URL flash sale target
    "chromedriver": "./webdriver/chromedriver.exe",
    "autoCheckout": true,                // true = auto checkout, false = stop di cart
    "autoOrder": false,                  // (Coming soon)
    "options": [],
    "modules": ["progress", "inquirer", "selenium", "colorama", "requests", "wget"]
}
```

---

## 🤝 Kontribusi

Pull requests welcome! Untuk perubahan besar:
1. Fork repo
2. Buat branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📜 License

Distributed under the **MIT License**. Lihat `LICENSE` untuk detail.

---

## 👤 Author

**YOS** — [@yosyoss](https://github.com/yosyoss)

---

## 🙏 Acknowledgments

- Built with [Selenium](https://selenium-python.readthedocs.io/) + [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- Tested on Windows 11 + Chrome 150
- Inspired by Indonesian flash sale community

---

> ⚡ **Pro tip:** Untuk akurasi milidetik, tekan **Enter** di terminal di detik terakhir (00:00:01) timer Shopee. Lebih cepat dari auto-detect.

> 📌 **Disclaimer kedua:** Saya tidak bertanggung jawab atas account suspension atau kerugian dari penggunaan bot ini. Gunakan secara bertanggung jawab.
