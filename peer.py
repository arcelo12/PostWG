import json
import os
from utils import send_discord_notification
from pgsql import get_db_peers

# Load konfigurasi
base_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(base_dir, "config.json")

with open(config_path, "r") as f:
    config = json.load(f)

SERVERS = config["servers"]
DISCORD_WEBHOOK = config["discord_webhook"]

def sync_wireguard():
    for server in SERVERS:
        if server == "debian-native":
            from linux.debian_native import sync_wireguard as debian_native_sync
            try:
                debian_native_sync()
            except Exception as e:
                print(f"Error on {server}: {e}")
                send_discord_notification(f"⚠️ Gagal melakukan sinkronisasi WireGuard pada {server}: {e}")
        elif server == "debian-ssh":
            from linux.debian_ssh import DebianSSH
            for ssh_config in config["debian"]["ssh"]:
                debian_ssh = DebianSSH(ssh_config)
                try:
                    debian_ssh.sync_wireguard()
                except Exception as e:
                    print(f"Error on {server} ({ssh_config['host']}): {e}")
                    send_discord_notification(f"⚠️ Gagal melakukan sinkronisasi WireGuard pada {server} ({ssh_config['host']}): {e}")
        elif server == "mikrotik":
            from mikrotik import Mikrotik
            for mikrotik_config in config["mikrotik"]:
                mikrotik = Mikrotik(mikrotik_config)
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
                            mikrotik.add_wireguard_peer(name, public_key, allowed_ip, mikrotik_config["interface"])

                    # Hapus peer yang tidak ada di database
                    for peer in wg_peers:
                        if (peer["public-key"], peer["name"]) not in db_peer_keys:
                            mikrotik.delete_wireguard_peer(peer["public-key"], peer["name"], mikrotik_config["interface"])

                    # Kirim notifikasi
                    send_discord_notification(f"✅ Sinkronisasi WireGuard selesai pada {mikrotik_config['name']} ({mikrotik_config['host']}).")
                except Exception as e:
                    print(f"Error on {server} ({mikrotik_config['host']}): {e}")
                    send_discord_notification(f"⚠️ Gagal melakukan sinkronisasi WireGuard pada {mikrotik_config['name']} ({mikrotik_config['host']}): {e}")
                finally:
                    mikrotik.ssh_close()

def check_status():
    for server in SERVERS:
        if server == "debian-native":
            from linux.debian_native import check_status as debian_native_check
            try:
                debian_native_check()
            except Exception as e:
                print(f"Error on {server}: {e}")
                send_discord_notification(f"⚠️ Gagal mengecek status WireGuard pada {server}: {e}")
        elif server == "debian-ssh":
            from linux.debian_ssh import DebianSSH
            for ssh_config in config["debian"]["ssh"]:
                debian_ssh = DebianSSH(ssh_config)
                try:
                    debian_ssh.check_status()
                except Exception as e:
                    print(f"Error on {server} ({ssh_config['host']}): {e}")
                    send_discord_notification(f"⚠️ Gagal mengecek status WireGuard pada {server} ({ssh_config['host']}): {e}")
        elif server == "mikrotik":
            from mikrotik import Mikrotik
            for mikrotik_config in config["mikrotik"]:
                mikrotik = Mikrotik(mikrotik_config)
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
                    total_peers = mikrotik.get_total_peers(mikrotik_config["interface"])
                    print(f"Total Peers: {total_peers}")

                    # Kirim notifikasi ke Discord jika webhook diatur
                    send_discord_notification(f"WireGuard Status pada {mikrotik_config['name']} ({mikrotik_config['host']}):\n```{formatted_status}```\nTotal Peers: {total_peers}")

                except Exception as e:
                    print(f"Error on {server} ({mikrotik_config['host']}): {e}")
                    send_discord_notification(f"⚠️ Gagal mengecek status WireGuard pada {mikrotik_config['name']} ({mikrotik_config['host']}): {e}")
                finally:
                    mikrotik.ssh_close()

if __name__ == "__main__":
    sync_wireguard()