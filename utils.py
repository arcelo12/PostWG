import requests
import json
import os

# Load konfigurasi
base_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(base_dir, "config.json")

with open(config_path, "r") as f:
    config = json.load(f)

DISCORD_WEBHOOK = config["discord_webhook"]

def send_discord_notification(message):
    """Mengirim notifikasi ke Discord"""
    if not DISCORD_WEBHOOK:
        print("❌ Webhook Discord tidak diatur.")
        return

    data = {
        "content": message
    }

    try:
        response = requests.post(DISCORD_WEBHOOK, json=data)
        if response.status_code == 204:
            print("✅ Notifikasi berhasil dikirim ke Discord.")
        else:
            print(f"❌ Gagal mengirim notifikasi ke Discord: {response.status_code}")
    except Exception as e:
        print(f"❌ Terjadi kesalahan saat mengirim notifikasi ke Discord: {e}")