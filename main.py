import time
import threading
import json
from utils import Utils
from peer import sync_wireguard, check_status
from linux.debian_ssh import DebianSSH
from pgsql import DB

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
DISCORD_WEBHOOK = config["discord_webhook"]

# Initialize Utils
utils = Utils(DISCORD_WEBHOOK)

# Initialize Database
db = DB(config["database"])

def save_config():
    """Menyimpan konfigurasi ke config.json"""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def sync_job():
    """Looping sinkronisasi otomatis"""
    while config["cron"]["enabled"]:
        print("\n🔄 Menjalankan sinkronisasi otomatis...")
        sync_wireguard(config, db, utils)
        time.sleep(SYNC_INTERVAL)

def status_job():
    """Looping pengecekan status otomatis"""
    while config["cron"]["enabled"]:
        print("\n🔍 Mengecek status WireGuard otomatis...")
        check_status(config, db, utils)
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

def check_and_create_wg_conf():
    """Memeriksa dan membuat file wg.conf di server Debian jika belum ada"""
    for server in config["servers"]:
        if server["type"] == "debian-ssh":
            debian_ssh = DebianSSH(server)
            debian_ssh.ssh_connect()
            try:
                # Periksa apakah file wg.conf sudah ada
                command = "test -f /etc/wireguard/wg.conf && echo 'exists' || echo 'not exists'"
                result = debian_ssh.execute_command(command)
                if "not exists" in result:
                    print(f"File wg.conf tidak ditemukan di {server['host']}.")
                    choice = input(f"Apakah Anda ingin membuat file wg.conf di {server['host']}? (y/n): ").strip().lower()
                    if choice == 'y':
                        # Buat file wg.conf
                        create_command = "echo '[Interface]\nPrivateKey = <your-private-key>\nAddress = <your-address>\n\n[Peer]\nPublicKey = <peer-public-key>\nAllowedIPs = <peer-allowed-ips>' > /etc/wireguard/wg.conf"
                        debian_ssh.execute_command(create_command)
                        print(f"✅ File wg.conf berhasil dibuat di {server['host']}.")
                    else:
                        print(f"❌ Pembuatan file wg.conf dibatalkan di {server['host']}.")
                else:
                    print(f"✅ File wg.conf sudah ada di {server['host']}.")
            except Exception as e:
                print(f"Error: {e}")
            finally:
                debian_ssh.ssh_close()

if __name__ == "__main__":
    while True:
        print("\n=== WireGuard Sync Manager ===")
        print("1️⃣  Sinkronisasi Sekarang")
        print("2️⃣  Cek Status WireGuard")
        print("3️⃣  Toggle Cron Job (ON/OFF)")
        print("4️⃣  Periksa dan Buat wg.conf di Debian")
        print("5️⃣  Keluar")

        choice = input("Pilih opsi (1/2/3/4/5): ").strip()

        if choice == "1":
            for server, i in enumerate(config["servers"], start=1):
                threading.Thread(target=sync_wireguard(config,db,utils), daemon=True).start() #Thread daemonized
            # sync_wireguard(config, db, utils) # Only for testing purpose, please change to sync_job() after finish testing.
        elif choice == "2":
            check_status(config, db, utils) # Only for testing purpose, please change to status_job() after finish testing.
        elif choice == "3":
            toggle_cron()
        elif choice == "4":
            check_and_create_wg_conf()
        elif choice == "5":
            print("🚪 Keluar dari program.")
            break
        else:
            print("❌ Pilihan tidak valid!")

    start_cron()  # Jalankan cron jika sudah aktif sebelumnya