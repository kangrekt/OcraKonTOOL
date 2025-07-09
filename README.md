# 🛠️ OcraKonTOOL

**OcraKonTOOL** adalah alat serbaguna otomatis berbasis Python untuk blockchain [Octra](https://octra.network/). Tool ini dibuat untuk membantu pengguna mengelola wallet, klaim faucet otomatis menggunakan CAPTCHA solver, serta mengirim OCT ke banyak alamat sekaligus.

---

## ✨ Fitur Utama

* 🔐 **Wallet Generator** – Membuat banyak wallet Octra (mnemonic + address + private key)
* 🧙 **Faucet Otomatis** – Klaim otomatis OCT dari faucet menggunakan 2Captcha
* 🌐 **Proxy Support** – Dukung rotating proxy (`http://ip:port`) via `proxies.txt`
* 🚀 **Multi Send** – Kirim OCT ke banyak alamat sekaligus dari banyak wallet
* 📊 **Saldo dan Nonce Checker** – Cek saldo OCT dan nonce via `octrascan.io`

---

## 📂 Struktur File Pendukung

| File               | Fungsi                                                      |
| ------------------ | ----------------------------------------------------------- |
| `wallet.json`      | File hasil pembuatan wallet Octra                           |
| `address.txt`      | File hasil pembuatan wallet Octra                 |
| `log.txt`          | Alamat random yang di hasilkan setiap transaksi             |
| `proxies.txt`      | `http://username:password@ip:host``http://ip:port`          |
| `Key_2captcha.txt` | API key untuk 2Captcha (digunakan untuk solve reCAPTCHA v2) |

---

## 🔧 Instalasi

### 1. Clone Repo

```bash
git clone https://github.com/kangrekt/OcraKonTOOL.git
cd OcraKonTOOL
```

### 2. Install Dependensi

```bash
pip install -r requirements.txt
```

Jika `requirements.txt` belum tersedia, install manual:

```bash
pip install base58 bip-utils pynacl aiohttp requests beautifulsoup4 colorama twocaptcha
```
Masuk mode venv

```bash
python3 -m venv venv
source venv/bin/activate
```
---

## 🚀 Cara Menjalankan

```bash
python3 octratool.py
```

### Menu

```
1. Buat Wallet     → Generate wallet baru Octra
2. Faucet          → Klaim faucet otomatis (3 metode tersedia)
3. Multi Send      → Kirim OCT ke banyak alamat
0. Keluar
```

---

## ⚙️ Konfigurasi Proxy & CAPTCHA

### 🔐 File `Key_2captcha.txt`

Isi file dengan 1 baris API key dari [2captcha.com](https://2captcha.com/):

```text
your_2captcha_api_key_here
```

### 🌍 File `proxies.txt` (opsional)

Gunakan jika ingin menjalankan klaim dengan proxy:

```text
http://123.456.789.000:8080
http://1.2.3.4:3128
```

Saat menjalankan metode faucet, Anda akan ditanya:

> "Pakai Proxy (y/n)?"

---

## 📝 Contoh Output Wallet

```json
{
  "priv": "base64_private_key",
  "addr": "oct1xyzAbCDEf...",
  "mnemonic": "word1 word2 word3 ... word24"
}
```

---

## ⚠️ Catatan Penting

* Gunakan Screen untuk running background
* Faucet bisa gagal jika saldo habis → akan muncul pesan `"Insufficient balance"`
* Gunakan proxy unik jika klaim massal dari banyak address
* Private key disimpan tanpa enkripsi – simpan file `wallet.json` dengan sangat hati-hati!

---

## 📜 Lisensi

MIT License © 2025 [@kangrekt](https://github.com/kangrekt)

---

## ☕ Dukungan

Jika proyek ini membantumu, bantu dengan:

* ⭐ Memberi bintang di GitHub
* 🏱 Kontribusi pull request / ide baru
* 📣 Share ke komunitas lain

---
