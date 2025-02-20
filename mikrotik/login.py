import paramiko
import json
import os

# Load konfigurasi
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_path = os.path.join(base_dir, "config.json")

with open(config_path, "r") as f:
    config = json.load(f)

MIKROTIK_CONFIG = config["mikrotik"]

def connect_ssh():
    """Membuat koneksi SSH ke MikroTik"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"🔄 Menghubungkan ke MikroTik {MIKROTIK_CONFIG['host']}:{MIKROTIK_CONFIG['port']}...")
        ssh.connect(
            hostname=MIKROTIK_CONFIG["host"],
            port=MIKROTIK_CONFIG["port"],
            username=MIKROTIK_CONFIG["user"],
            password=MIKROTIK_CONFIG["password"]
        )
        print("✅ Koneksi SSH berhasil!")
        return ssh
    except Exception as e:
        print(f"❌ Gagal menghubungkan ke MikroTik: {e}")
        raise e

def test_ssh_connection():
    """Menguji koneksi SSH ke MikroTik"""
    ssh = connect_ssh()
    ssh.close()

if __name__ == "__main__":
    test_ssh_connection()