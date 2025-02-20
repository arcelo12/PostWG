from mikrotik import Mikrotik
from pgsql import get_db_peers
from utils import send_discord_notification
import json
import os

# Load konfigurasi
base_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(base_dir, "config.json")

with open(config_path, "r") as f:
    config = json.load(f)

INTERFACE = config["mikrotik"]["interface"]

def sync_wireguard():
    mikrotik = Mikrotik()
    mikrotik.ssh_connect()

    try:
        # Ambil data dari database
        db_peers = get_db_peers()

        # Ambil daftar peer yang ada di WireGuard
        wg_peers = mikrotik.get_wireguard_status()
        wg_peer_keys = {(peer["public-key"], peer["name"]) for peer in wg_peers}

        # Sinkronisasi: Tambah peer baru, hapus peer lama
        db_peer_keys = {(peer[1], peer[0]) for peer in db_peers}  # Menggunakan name sebagai kunci

        # Tambah peer yang belum ada di WireGuard
        for name, public_key, allowed_ip in db_peers:
            if (public_key, name) not in wg_peer_keys:
                mikrotik.add_wireguard_peer(name, public_key, allowed_ip, INTERFACE)

        # Hapus peer yang tidak ada di database
        for peer in wg_peers:
            if (peer["public-key"], peer["name"]) not in db_peer_keys:
                mikrotik.delete_wireguard_peer(peer["public-key"], peer["name"], INTERFACE)

        # Kirim notifikasi
        send_discord_notification("✅ Sinkronisasi WireGuard selesai.")
    except Exception as e:
        print(f"Error: {e}")
        send_discord_notification(f"⚠️ Gagal melakukan sinkronisasi WireGuard: {e}")
    finally:
        mikrotik.ssh_close()

def check_status():
    mikrotik = Mikrotik()
    mikrotik.ssh_connect()

    try:
        # Dapatkan status WireGuard dari MikroTik
        status_output = mikrotik.get_wireguard_status()

        # Format hasil
        formatted_status = "\n".join(
            [f"Peer: {peer['name']}, Public Key: {peer['public-key']}, Allowed IP: {peer['allowed-address']}" for peer in status_output]
        )

        print("WireGuard Status:\n", formatted_status)

        # Dapatkan total peers dari MikroTik
        total_peers = mikrotik.get_total_peers(INTERFACE)
        print(f"Total Peers: {total_peers}")

        # Kirim notifikasi ke Discord jika webhook diatur
        send_discord_notification(f"Total Peers: {total_peers}")
    except Exception as e:
        print(f"Error: {e}")
        send_discord_notification(f"⚠️ Gagal mengecek status WireGuard: {e}")
    finally:
        mikrotik.ssh_close()