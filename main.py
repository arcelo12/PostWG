import time
import threading
import json
import os
from peer import sync_wireguard, check_status

# Load konfigurasi dari config.json
CONFIG_FILE = "config.json"

def load_config():
    """Membaca konfigurasi dari config.json"""
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

config = load_config()
SYNC_INTERVAL = config["cron"]["interval_minutes"] * 60
STATUS_INTERVAL = SYNC_INTERVAL
CRON_ENABLED = config["cron"]["enabled"]

def save_config():
    """Menyimpan konfigurasi ke config.json"""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def sync_job():
    """Looping sinkronisasi otomatis"""
    while config["cron"]["enabled"]:
        print("\n🔄 Menjalankan sinkronisasi otomatis...")
        sync_wireguard()
        time.sleep(SYNC_INTERVAL)

def status_job():
    """Looping pengecekan status otomatis"""
    while config["cron"]["enabled"]:
        print("\n🔍 Mengecek status WireGuard otomatis...")
        check_status()
        time.sleep(STATUS_INTERVAL)

def start_cron():
    """Memulai cron jika diaktifkan"""
    if config["cron"]["enabled"]:
        threading.Thread(target=sync_job, daemon=True).start()
        threading.Thread(target=status_job, daemon=True).start()
        print("✅ Cron job AKTIF!")

def toggle_cron():
    """Mengaktifkan/Mematikan cron"""
    config["cron"]["enabled"] = not config["cron"]["enabled"]
    save_config()

    if config["cron"]["enabled"]:
        print("✅ Cron job diaktifkan!")
        start_cron()
    else:
        print("⛔ Cron job dimatikan!")

if __name__ == "__main__":
    while True:
        print("\n=== WireGuard Sync Manager ===")
        print("1️⃣  Sinkronisasi Sekarang")
        print("2️⃣  Cek Status WireGuard")
        print("3️⃣  Toggle Cron Job (ON/OFF)")
        print("4️⃣  Keluar")

        choice = input("Pilih opsi (1/2/3/4): ").strip()

        if choice == "1":
            sync_wireguard()
        elif choice == "2":
            check_status()
        elif choice == "3":
            toggle_cron()
        elif choice == "4":
            print("🚪 Keluar dari program.")
            break
        else:
            print("❌ Pilihan tidak valid!")

    start_cron()  # Jalankan cron jika sudah aktif sebelumnya