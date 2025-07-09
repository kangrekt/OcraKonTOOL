import base64
import hashlib
import json
import sys
import os
from typing import List, Dict, Any, Tuple
from colorama import Fore, Style, init
import time
import asyncio
import aiohttp
import re
import random
from bs4 import BeautifulSoup
from nacl.signing import SigningKey
import requests
from bip_utils import Bip39MnemonicGenerator, Bip39SeedGenerator
import base58
from datetime import datetime
import nacl

# Konfigurasi
c = {'r': '\033[0m', 'g': '\033[32m', 'y': '\033[33m', 'R': '\033[31m'}
priv, addr = None, None
sk, pub = None, None
b58 = re.compile(r"^oct[1-9A-HJ-NP-Za-km-z]{44,}$")
μ = 1_000_000
session = None
rpc = "https://octra.network"

# Inisialisasi colorama
init()

try:
    import base58
    from bip_utils import Bip39MnemonicGenerator, Bip39SeedGenerator
    from nacl.signing import SigningKey
    import nacl
except ImportError as e:
    print("\n❌ Error: Package yang diperlukan tidak ditemukan.")
    print("Silakan instal package yang diperlukan dengan perintah:")
    print("pip install base58 bip-utils pynacl")
    print(f"\nError detail: {str(e)}")
    sys.exit(1)

class OctraTool:
    def __init__(self):
        self.wallets: List[Dict[str, Any]] = []
        self.current_wallet = None

    def generate_wallet(self, prefix: str = "oct") -> Dict[str, Any]:
        """Generate a new wallet with mnemonic, private key, and address"""
        try:
            # Generate mnemonic (24 kata)
            mnemonic = Bip39MnemonicGenerator().FromWordsNumber(24)
            mnemonic_str = str(mnemonic)
            
            # Generate seed dari mnemonic
            seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
            
            # Generate signing key
            signing_key = SigningKey(seed_bytes[:32])
            
            # Generate public key
            pub_key_bytes = signing_key.verify_key.encode()
            
            # Generate address
            sha_pub = hashlib.sha256(pub_key_bytes).digest()
            address_body = base58.b58encode(sha_pub).decode('utf-8')
            address = prefix + address_body
            
            # Return wallet dengan format yang diinginkan
            return {
                "priv": base64.b64encode(signing_key.encode()).decode(),
                "addr": address,
                "mnemonic": mnemonic_str
            }
        except Exception as e:
            print(f"❌ Error saat membuat wallet: {str(e)}")
            return None

    def save_wallets_json(self, wallets: List[Dict[str, Any]]) -> None:
        """Save wallets to JSON file"""
        # Menyimpan semua wallet dalam format array
        with open("wallet.json", "w") as f:
            json.dump(wallets, f, indent=4)
        print("\n📂 File JSON berhasil disimpan: wallet.json")

    def save_wallets_txt_components(self, wallets: List[Dict[str, Any]]) -> None:
        """Save mnemonics and addresses to text files"""
        try:
            with open("mnemonic.txt", "w", encoding="utf-8") as f_mnemonic, \
                 open("address.txt", "w", encoding="utf-8") as f_addr:
                for wallet in wallets:
                    # Pastikan wallet memiliki semua field yang diperlukan
                    mnemonic = wallet.get("mnemonic", "")
                    addr = wallet.get("addr", "")
                    
                    if mnemonic:
                        f_mnemonic.write(mnemonic + "\n")
                    if addr:
                        f_addr.write(addr + "\n")
            
            print("📝 Daftar mnemonic disimpan di: mnemonic.txt")
            print("📍 Daftar alamat disimpan di: address.txt")
        except Exception as e:
            print(f"❌ Error saat menyimpan file: {str(e)}")

    def save_to_log(self, address: str) -> None:
        """Menyimpan satu alamat terbaru di log.txt"""
        try:
            # Hapus file log.txt yang lama jika ada
            if os.path.exists("log.txt"):
                os.remove("log.txt")
            
            # Buat file baru dengan alamat baru
            with open("log.txt", "w", encoding="utf-8") as f:
                f.write(address + "\n")
            
        except Exception as e:
            print(f"❌ Error saat menyimpan ke log.txt: {str(e)}")

    def create_wallets(self) -> None:
        """Create new wallets"""
        try:
            print("\n✨ OCTRA Wallet Generator ✨")
            print("=" * 50)
            count = int(input("\n🚀 Masukkan jumlah wallet yang ingin dibuat: ").strip())
            if count < 1:
                raise ValueError("Jumlah wallet harus lebih dari 0")
                
            prefix = "oct"
            self.wallets = [self.generate_wallet(prefix) for _ in range(count)]
            
            self.save_wallets_json(self.wallets)
            self.save_wallets_txt_components(self.wallets)
            
            print("\n" + "=" * 50)
            print(f"🎉 SUKSES! {count} wallet baru telah berhasil dibuat!")
            print("=" * 50)
            print("\n📋 Detail wallet tersimpan di file berikut:"
                  "\n   • wallet.json    - Data wallet"
                  "\n   • mnemonic.txt   - Data wallet"
                  "\n   • address.txt    - Alamat wallet")
            print("\n🔐 Simpan file-file ini di tempat yang aman!")
            
        except ValueError as ve:
            print(f"\n❌ Error: {ve}")
        except Exception as e:
            print(f"\n❌ Terjadi kesalahan: {str(e)}")

    def metod_1(self) -> None:
        """Metod 1 faucet functionality"""
        import requests
        import random
        import time
        import sys
        from datetime import datetime

        # Load 2Captcha API key
        try:
            with open('Key_2captcha.txt', 'r') as f:
                API_KEY_2CAPTCHA = f.readline().strip()
                if not API_KEY_2CAPTCHA:
                    print("\n❌ Error: File Key_2captcha.txt kosong")
                    return
        except FileNotFoundError:
            print("\n❌ Error: File Key_2captcha.txt tidak ditemukan")
            return

        # Configuration
        SITE_KEY = "6LfeWHYrAAAAABi7KV7jwT6pwlq-Ep7A1pWnse1l"
        CLAIM_URL = "https://faucet.octra.network/claim"
        CLAIM_PAGE_URL = "https://faucet.octra.network/"

        def log(message, level="info"):
            timestamp = datetime.now().strftime("%H:%M:%S")
            emoji = {
                "info": "ℹ️ ", "success": "✅ ", "warning": "⚠️ ",
                "error": "❌ ", "debug": "🔍 ", "captcha": "🧩 ",
                "process": "🔄 ", "header": "🚀 ", "address": "📍",
                "proxy": "🌐 ", "time": "⏳ "
            }
            if level in emoji:
                formatted_msg = f"[{timestamp}]{emoji[level]}{message}"
            else:
                formatted_msg = f"[{timestamp}]{message}"
            print(formatted_msg)

        def solve_captcha(api_key):
            log("Mengirim permintaan CAPTCHA ke 2Captcha...", "captcha")
            try:
                send = requests.post("http://2captcha.com/in.php", 
                    data={
                        "key": api_key,
                        "method": "userrecaptcha",
                        "googlekey": SITE_KEY,
                        "pageurl": CLAIM_PAGE_URL,
                        "json": 1
                    }, timeout=30).json()
                if send.get("status") != 1:
                    log(f"Gagal mengirim CAPTCHA: {send.get('request', 'Tidak ada pesan error')}", "error")
                    return None

                captcha_id = send["request"]
                log(f"CAPTCHA ID: {captcha_id}", "captcha")

                spinner = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
                for i in range(60):
                    sys.stdout.write(f"\r{spinner[i % len(spinner)]} Memproses CAPTCHA...")
                    sys.stdout.flush()
                    time.sleep(5)
                    try:
                        res = requests.get(
                            f"http://2captcha.com/res.php?key={api_key}&action=get&id={captcha_id}&json=1",
                            timeout=30).json()
                        if res.get("status") == 1:
                            sys.stdout.write("\r" + " "*50 + "\r")
                            log("CAPTCHA berhasil diselesaikan!", "success")
                            return res["request"]
                        elif res.get("request") != "CAPCHA_NOT_READY":
                            sys.stdout.write("\r" + " "*50 + "\r")
                            log(f"Error CAPTCHA: {res.get('request', 'Tidak ada pesan error')}", "error")
                            return None
                    except Exception as e:
                        sys.stdout.write("\r" + " "*50 + "\r")
                        log(f"Error saat memeriksa CAPTCHA: {str(e)}", "error")
                        return None
                sys.stdout.write("\r" + " "*50 + "\r")
                log("Waktu tunggu CAPTCHA habis (5 menit)", "error")
                return None
            except Exception as e:
                log(f"Error saat mengirim CAPTCHA: {str(e)}", "error")
                return None

        def claim_faucet(address, captcha_token, proxy=None):
            log(f"Mulai klaim untuk {address}")
            boundary = "----WebKitFormBoundaryOw449LhgqfJ3hb1G"
            headers = {
                "content-type": f"multipart/form-data; boundary={boundary}",
                "origin": CLAIM_PAGE_URL,
                "referer": CLAIM_PAGE_URL,
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }

            data = (
                f"--{boundary}\r\n"
                f'Content-Disposition: form-data; name="address"\r\n\r\n'
                f"{address}\r\n"
                f"--{boundary}\r\n"
                f'Content-Disposition: form-data; name="is_validator"\r\n\r\n'
                f"false\r\n"
                f"--{boundary}\r\n"
                f'Content-Disposition: form-data; name="g-recaptcha-response"\r\n\r\n'
                f"{captcha_token}\r\n"
                f"--{boundary}--\r\n"
            )

            proxies = {"http": proxy, "https": proxy} if proxy else None

            try:
                resp = requests.post(CLAIM_URL, headers=headers, data=data.encode(), proxies=proxies, timeout=60)
                res_json = resp.json()
                if "Insufficient balance" in res_json.get("error", ""):
                    log("Faucet kehabisan saldo. Menghentikan script.", "error")
                    sys.exit(0)
                log(f"Sukses klaim: {res_json}", "success")
                return True
            except Exception as e:
                log(f"Gagal request: {e}", "error")
                return False

        def load_file_lines(filename):
            try:
                with open(filename, "r") as f:
                    return [line.strip() for line in f if line.strip()]
            except FileNotFoundError:
                return []

        print("\n=== Metod 1 ===\n")
        
        addresses = load_file_lines("address.txt")
        if not addresses:
            log("Tidak ditemukan alamat di address.txt", "error")
            return

        use_proxy = input("Pakai Proxy (y/n)? ").strip().lower() == "y"
        proxies = load_file_lines("proxies.txt") if use_proxy else []

        log("Mulai proses klaim...", "header")
        log(f"Total alamat: {len(addresses)}", "info")
        log(f"Total proxy: {len(proxies) if proxies else 'Tidak menggunakan proxy'}", "proxy")

        print("\n" + "-" * 50)
        log("Memulai klaim untuk setiap alamat...", "process")
        print("-" * 50 + "\n")

        success_addresses = []

        while addresses:
            addr = addresses.pop(0)
            proxy = random.choice(proxies) if proxies else None

            print(f"\n📌 ALAMAT YANG DIPROSES")
            log(f"Alamat: {addr}", "address")
            if proxy:
                log(f"Menggunakan proxy: {proxy}", "proxy")

            while True:
                captcha = solve_captcha(API_KEY_2CAPTCHA)
                if captcha:
                    try:
                        if claim_faucet(addr, captcha, proxy):
                            success_addresses.append(addr)
                            log("Klaim berhasil! Alamat ditambahkan ke daftar berhasil.", "success")
                            break
                        else:
                            log("Gagal mengklaim, mencoba lagi...", "warning")
                            time.sleep(5)
                    except Exception as e:
                        log(f"Error saat klaim: {str(e)}", "error")
                        log("Akan dicoba lagi dalam 5 detik...", "warning")
                        time.sleep(5)
                else:
                    log("Gagal mendapatkan CAPTCHA", "warning")
                    time.sleep(5)

            if addresses:
                delay = random.randint(10, 20)
                log(f"Menunggu {delay} detik sebelum akun berikutnya...", "time")
                time.sleep(delay)

        print("\n")
        log("SEMUA PROSES TELAH SELESAI", "header")
        log(f"✅Alamat yang berhasil: {len(success_addresses)}", "success")
        log(f"❌Alamat yang gagal: {len(addresses)}", "error")
        print()

    def metod_2(self) -> None:
        """Metod 2 faucet functionality"""
        import requests
        import time
        from twocaptcha import TwoCaptcha

        # Load 2Captcha API key
        try:
            with open('Key_2captcha.txt', 'r') as f:
                API_KEY_2CAPTCHA = f.readline().strip()
                if not API_KEY_2CAPTCHA:
                    print("\n❌ Error: File Key_2captcha.txt kosong")
                    return
        except FileNotFoundError:
            print("\n❌ Error: File Key_2captcha.txt tidak ditemukan")
            return
            
        # Config
        FAUCET_URL = 'https://api-oct-faucet.xme.my.id/api/faucet/claim'
        SITE_KEY = "6Lcu8IYqAAAAAItJizqGZKh2542ecWWNlElYKOrS"
        PAGE_URL = "https://oct-faucet.xme.my.id"
        MAX_RETRIES = 3

        def log(icon: str, message: str) -> None:
            print(f"[{icon}] {message}")

        def load_file_lines(filename: str) -> list:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    return [line.strip() for line in f if line.strip()]
            except FileNotFoundError:
                return []

        def solve_captcha(solver: TwoCaptcha) -> str:
            log("⏳", "Meminta token CAPTCHA dari 2Captcha...")
            try:
                result = solver.recaptcha(sitekey=SITE_KEY, url=PAGE_URL)
                token = result.get('code')
                if token:
                    log("✅", "Token CAPTCHA berhasil.")
                    return token
                else:
                    log("❌", "Token CAPTCHA tidak valid")
                    return ""
            except Exception as e:
                log("❌", f"Gagal mendapatkan token CAPTCHA: {e}")
                return ""

        print("\n=== Metod 2 ===")
        
        # Load addresses
        addresses = load_file_lines("address.txt")
        if not addresses:
            log("❌", "Tidak ada address yang ditemukan di address.txt")
            return

        # Load proxies
        proxies = load_file_lines("proxies.txt")
        use_proxy = input("Pakai Proxy (y/n)? ").strip().lower() == 'y'
        
        solver = TwoCaptcha(API_KEY_2CAPTCHA)
        total_addresses = len(addresses)
        total_proxies = len(proxies)

        for i, address in enumerate(addresses, start=1):
            retries = 0
            success = False
            
            while retries < MAX_RETRIES and not success:
                # Setup proxy
                proxy = None
                if use_proxy and proxies:
                    proxy = proxies[(i-1) % total_proxies] if total_proxies > 1 else proxies[0]
                    proxies_dict = {"http": proxy, "https": proxy}
                    log("🌍", f"Proxy: {proxy}")
                else:
                    proxies_dict = None
                    log("🌍", "Tanpa Proxy")

                log("🚀", f"{i}. Memproses address: {address} (Retry {retries + 1}/{MAX_RETRIES})")

                try:
                    # Solve CAPTCHA
                    recaptcha_token = solve_captcha(solver)
                    if not recaptcha_token:
                        raise ValueError("Gagal mendapatkan token CAPTCHA")

                    # Prepare request
                    payload = {"address": address, "recaptchaToken": recaptcha_token}
                    headers = {
                        "accept": "*/*",
                        "content-type": "application/json",
                        "origin": PAGE_URL,
                        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
                    }

                    # Send request
                    response = requests.post(
                        FAUCET_URL,
                        headers=headers,
                        json=payload,
                        proxies=proxies_dict,
                        timeout=30
                    )
                    data = response.json()

                    if data.get("success"):
                        tx_hash = data.get("txHash", "N/A")
                        log("🎉", f"Sukses klaim: {address} → txHash: {tx_hash}")
                        success = True
                    else:
                        error = data.get("error", "Unknown error")
                        if "rate limit exceeded" in error.lower():
                            log("⏳", f"Rate limit terdeteksi, melewati address: {address}")
                            success = True
                        else:
                            raise Exception(error)

                except Exception as e:
                    log("❌", f"Error: {e}")
                    retries += 1
                    if retries < MAX_RETRIES:
                        delay = 5
                        log("⏳", f"Mencoba ulang dalam {delay} detik...")
                        time.sleep(delay)

            if not success:
                log("❌", f"Gagal setelah {MAX_RETRIES} kali percobaan untuk {address}")

            # Delay between addresses
            if i < total_addresses:
                time.sleep(5)

        print("\n✅ Proses selesai!")

    def metod_3(self) -> None:
        """Metod 3 faucet functionality"""

    @staticmethod
    async def create_tx(wallet: dict, to: str, amount: float, nonce: int) -> tuple:
        """Membuat transaksi baru"""
        tx = {
            "from": wallet['addr'],
            "to_": to,
            "amount": str(int(amount * 1_000_000)),
            "nonce": nonce,
            "ou": "1" if amount < 1000 else "3",
            "timestamp": time.time() + random.random() * 0.01
        }
        bl = json.dumps(tx, separators=(',', ':')).encode()
        sig = base64.b64encode(wallet['sk'].sign(bl).signature).decode()
        tx.update(signature=sig, public_key=wallet['pub'])
        return tx, hashlib.sha256(bl).hexdigest()

    @staticmethod
    async def get_balance(addr: str) -> Tuple[int, float]:
        """Mengambil saldo dan nonce dari alamat wallet"""
        try:
            url = f'https://octrascan.io/addr/{addr}'
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
            }
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, lambda: requests.get(url, headers=headers, timeout=10))

            if response.status_code != 200:
                print(f"❗ Error HTTP {response.status_code} saat mengambil data saldo untuk {addr[:10]}...")
                return None, None

            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()
            
            saldo_match = re.search(r"Balance:\s*([\d.]+)\s*OCT", text)
            nonce_match = re.search(r"Nonce:\s*(\d+)", text)

            if saldo_match and nonce_match:
                saldo = float(saldo_match.group(1))
                nonce = int(nonce_match.group(1))
                print(f"💰 Saldo: {saldo:.6f} OCT | 🔢 Nonce: {nonce}")
                return nonce, saldo
            else:
                print(f"⚠️ Tidak dapat menemukan saldo atau nonce untuk {addr[:10]}")
                return None, None
        except Exception as e:
            print(f"❌ Error saat memeriksa saldo untuk {addr[:10]}: {str(e)}")
            return None, None

    @staticmethod
    async def send_tx(tx: dict) -> tuple:
        """Mengirim transaksi ke RPC node"""
        try:
            global session
            if not session:
                session = aiohttp.ClientSession()
            
            url = f"{rpc}/send-tx"
            async with session.request('POST', url, json=tx) as resp:
                text = await resp.text()
                try:
                    data = json.loads(text)
                    if data and data.get('status') == 'accepted':
                        return True, data.get('tx_hash', '')
                    elif text.lower().startswith('ok'):
                        return True, text.split()[-1]
                    return False, text
                except:
                    return False, text
        except Exception as e:
            return False, str(e)

    async def multi_send(self) -> None:
        """Fungsi untuk melakukan multi send token ke beberapa alamat"""
        print("\n🚀 === OCTRA MULTI SENDER ===")
        await asyncio.sleep(1)

        # Load wallets dari file
        try:
            with open('wallet.json', 'r') as f:
                wallets = json.load(f)
                if not isinstance(wallets, list) or not all('priv' in w and 'addr' in w for w in wallets):
                    raise ValueError("Invalid wallet data format")
                for wallet in wallets:
                    priv = wallet.get('priv')
                    addr = wallet.get('addr')
                    if not all([priv, addr]):
                        raise ValueError("Invalid wallet data")
                    wallet['sk'] = nacl.signing.SigningKey(base64.b64decode(priv))
                    wallet['pub'] = base64.b64encode(wallet['sk'].verify_key.encode()).decode()
        except Exception as e:
            print(f"❌ Gagal memuat wallets: {e}")
            return

        print(f"📦 Jumlah wallet yang akan digunakan: {len(wallets)}")
        await asyncio.sleep(1)

        # Load target addresses dari file
        try:
            with open('log.txt', 'r') as f:
                addresses = [line.strip() for line in f if line.strip()]
                # Validasi setiap alamat
                valid_addresses = []
                for addr in addresses:
                    if b58.match(addr):
                        valid_addresses.append(addr)
                    else:
                        print(f"⚠️ Alamat tidak valid: {addr}")
                        await asyncio.sleep(1)
                addresses = valid_addresses
        except FileNotFoundError:
            print("📄 File log.txt tidak ditemukan!")
            await asyncio.sleep(1)
            return

        if not addresses:
            print("⚠️ Tidak ada alamat yang valid di file log.txt")
            await asyncio.sleep(1)
            return

        unique_addresses = list(dict.fromkeys(addresses))
        if len(addresses) != len(unique_addresses):
            print(f"🧹 Ditemukan {len(addresses) - len(unique_addresses)} alamat duplikat, dihapus.")
            await asyncio.sleep(1)
            addresses = unique_addresses

        # Input jumlah OCT
        try:
            amount = float(input("\n💸 Masukkan jumlah OCT per alamat: ").strip())
            if amount <= 0:
                print("⚠️ Jumlah harus lebih dari 0")
                return
        except ValueError:
            print("❗ Jumlah tidak valid")
            return

        print("\n🚚 Memulai pengiriman...")
        await asyncio.sleep(1)

        success = 0
        failed = 0

        # Proses setiap wallet dengan retry mechanism yang tidak terbatas
        for i, wallet in enumerate(wallets, 1):
            # Buat wallet baru sebelum transaksi
            print("\n🔄 BUAT WALLET BARU...")
            address = self.generate_wallet()['addr']
            self.save_to_log(address)
            print(f"🎉 Alamat target berhasil dibuat: {address}")
            await asyncio.sleep(2)

            addr = wallet['addr']
            wallet_success = False
            wallet_retry_count = 0
            max_wallet_retries = 5

            while not wallet_success and wallet_retry_count < max_wallet_retries:
                print(f"\n🔐 Wallet {i}/{len(wallets)} - Alamat: {addr}")
                await asyncio.sleep(1)

                try:
                    # Periksa saldo dan nonce
                    nonce, balance = await OctraTool.get_balance(addr)
                    if balance is None:
                        print(f"❌ Gagal mendapatkan saldo untuk wallet {i}")
                        await asyncio.sleep(2)
                        wallet_retry_count += 1
                        if wallet_retry_count >= max_wallet_retries:
                            print(f"❌ Wallet {i} mencapai batas maksimum percobaan ({max_wallet_retries} kali)")
                            wallet_failed = True
                            break
                        continue
                    
                    if balance < amount:
                        print(f"❌ Saldo tidak mencukupi! (Saldo: {balance:.6f} OCT | Dibutuhkan: {amount:.6f} OCT)")
                        await asyncio.sleep(1)
                        print(f"⏭️ Skip ke wallet berikutnya...")
                        await asyncio.sleep(1)
                        wallet_failed = True
                        break
                except Exception as e:
                    print(f"❌ Error saat memeriksa saldo: {str(e)}")
                    await asyncio.sleep(1)
                    wallet_retry_count += 1
                    if wallet_retry_count >= max_wallet_retries:
                        print(f"❌ Wallet {i} mencapai batas maksimum percobaan ({max_wallet_retries} kali)")
                        wallet_failed = True
                        break

                try:
                    retry_count = 0
                    tx_success = False

                    max_retries = 3  

                    all_transactions_success = True
                    for j, to in enumerate(addresses, 1):
                        tx_retry_count = 0
                        tx_success = False

                        while not tx_success and tx_retry_count < max_retries:
                            try:
                                tx_nonce = nonce + j
                                print(f"\n📤 Mengirim {amount:.6f} OCT ke {to[:10]}...")
                                await asyncio.sleep(1)

                                tx, _ = await OctraTool.create_tx(wallet, to, amount, tx_nonce)
                                response = await OctraTool.send_tx(tx)
                                ok, result = response

                                if ok:
                                    print(f"✅ Berhasil! 🔗 Hash: {result}")
                                    await asyncio.sleep(1)
                                    success += 1
                                    tx_success = True
                                    break
                                else:
                                    error_msg = str(result).lower()
                                    print(f"❌ Gagal: {result}")
                                    await asyncio.sleep(1)

                                    if "duplicate" in error_msg or "nonce" in error_msg:
                                        print("⚠️ Nonce sudah digunakan, mencoba dengan nonce yang lebih tinggi...")
                                        await asyncio.sleep(1)
                                        nonce += 1
                                        tx_retry_count += 1
                                        await asyncio.sleep(2)
                                        continue
                                    
                                    all_transactions_success = False
                                    break

                            except Exception as e:
                                print(f"🚫 Error: {str(e)}")
                                await asyncio.sleep(1)
                                tx_retry_count += 1
                                await asyncio.sleep(2)
                        else:
                            print(f"❌ Gagal setelah {max_retries} kali mencoba untuk transaksi dari {addr[:10]} ke {to[:10]}")
                            await asyncio.sleep(1)
                            all_transactions_success = False

                        await asyncio.sleep(1)

                    if all_transactions_success:
                        wallet_success = True
                        await asyncio.sleep(1)
                        break
                    else:
                        print(f"🔄 Wallet {i} gagal, mencoba ulang... (Percobaan {wallet_retry_count + 1}/{max_wallet_retries})")
                        await asyncio.sleep(2)
                        wallet_retry_count += 1

                except Exception as e:
                    print(f"❌ Error saat mengirim transaksi: {str(e)}")
                    await asyncio.sleep(1)
                    all_transactions_success = False

                    await asyncio.sleep(1)

                if all_transactions_success:
                    wallet_success = True
                    await asyncio.sleep(1)
                    break
                else:
                    print(f"🔄 Wallet {i} gagal, mencoba ulang... (Percobaan {wallet_retry_count + 1}/{max_wallet_retries})")
                    await asyncio.sleep(2)
                    wallet_retry_count += 1

                await asyncio.sleep(3)

            if wallet_success:
                await asyncio.sleep(5)
                print("📈 Lanjut Ke wallet berikutnya..")
                await asyncio.sleep(1)

            await asyncio.sleep(2)

        print(f"🏁 Selesai!")
        await asyncio.sleep(1)
        print(f"📈 Berhasil: {success}")
        await asyncio.sleep(1)

    def faucet(self) -> None:
        """Faucet menu"""
        print("\n=== FAUCET MENU ===")
        print("1. Metod 1")
        print("2. Metod 2")
        print("3. Metod 3")
        print("0. Kembali")
        
        choice = input("\nPilih metod (0-3): ").strip()
        
        if choice == "1":
            self.metod_1()
        elif choice == "2":
            self.metod_2()
        elif choice == "3":
            self.metod_3()
        elif choice != "0":
            print("❌ Pilihan tidak valid!")

    def show_menu(self) -> None:
        """Show main menu"""
        while True:
            print("\n" + "=" * 30)
            print("🛠️  OCTRA TOOL")
            print("=" * 30)
            print("1. Buat Wallet")
            print("2. Faucet")
            print("3. Multi Send")
            print("0. Keluar")
            
            try:
                choice = input("\nPilih menu (0-3): ").strip()
                
                if choice == "1":
                    self.create_wallets()
                elif choice == "2":
                    self.faucet()
                elif choice == "3":
                    asyncio.run(self.multi_send())
                elif choice == "0":
                    print("\n👋 Sampai jumpa!")
                    break
                else:
                    print("\n⚠️  Pilihan tidak valid!")
                    
            except KeyboardInterrupt:
                print("\n\n❌ Operasi dibatalkan")
                break
            except Exception as e:
                print(f"\n❌ Terjadi kesalahan: {str(e)}")

def main():
    tool = OctraTool()
    tool.show_menu()

if __name__ == "__main__":
    main()
