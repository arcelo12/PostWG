import requests

class Utils:
    def __init__(self, discord_webhook):
        self.DISCORD_WEBHOOK = discord_webhook

    def send_discord_notification(self, message):
        """Mengirim notifikasi ke Discord"""
        if not self.DISCORD_WEBHOOK:
            print("❌ Webhook Discord tidak diatur.")
            return

        data = {
            "content": message
        }

        try:
            response = requests.post(self.DISCORD_WEBHOOK, json=data)
            if response.status_code == 204:
                print("✅ Notifikasi berhasil dikirim ke Discord.")
            else:
                print(f"❌ Gagal mengirim notifikasi ke Discord: {response.status_code}")
        except Exception as e:
            print(f"❌ Terjadi kesalahan saat mengirim notifikasi ke Discord: {e}")