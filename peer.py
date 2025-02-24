from utils import send_discord_notification
from linux.debian_ssh import DebianSSH
from linux.debian_native import sync_wireguard as debian_native_sync, check_status as debian_native_check
from mikrotik import Mikrotik

def sync_wireguard(config, db):
    for server in config["servers"]:
        if server["type"] == "debian-native":
            try:
                debian_native_sync(server["interface"], db)
            except Exception as e:
                print(f"Error on {server['name']}: {e}")
                send_discord_notification(f"⚠️ Gagal melakukan sinkronisasi WireGuard pada {server['name']}: {e}")
        elif server["type"] == "debian-ssh":
            debian_ssh = DebianSSH(server, db)
            try:
                debian_ssh.sync_wireguard()
            except Exception as e:
                print(f"Error on {server['name']} ({server['host']}): {e}")
                send_discord_notification(f"⚠️ Gagal melakukan sinkronisasi WireGuard pada {server['name']} ({server['host']}): {e}")
        elif server["type"] == "mikrotik":
            mikrotik = Mikrotik(server)
            mikrotik.ssh_connect()
            try:
                # Ambil data dari database
                db_peers = db.get_peers()

                # Ambil daftar peer yang ada di WireGuard
                wg_peers = mikrotik.get_wireguard_status()
                wg_peer_keys = {(peer["public-key"], peer["name"]) for peer in wg_peers}

                # Sinkronisasi: Tambah peer baru, hapus peer lama
                db_peer_keys = {(peer[1], peer[0]) for peer in db_peers}  # Menggunakan name sebagai kunci

                # Tambah peer yang belum ada di WireGuard
                for name, public_key, allowed_ip in db_peers:
                    if (public_key, name) not in wg_peer_keys:
                        mikrotik.add_wireguard_peer(name, public_key, allowed_ip, server["interface"])

                # Hapus peer yang tidak ada di database
                for peer in wg_peers:
                    if (peer["public-key"], peer["name"]) not in db_peer_keys:
                        mikrotik.delete_wireguard_peer(peer["public-key"], peer["name"], server["interface"])

                # Kirim notifikasi
                send_discord_notification(f"✅ Sinkronisasi WireGuard selesai pada {server['name']} ({server['host']}).")
            except Exception as e:
                print(f"Error on {server['name']} ({server['host']}): {e}")
                send_discord_notification(f"⚠️ Gagal melakukan sinkronisasi WireGuard pada {server['name']} ({server['host']}): {e}")
            finally:
                mikrotik.ssh_close()

def check_status(config, db):
    for server in config["servers"]:
        if server["type"] == "debian-native":
            try:
                debian_native_check(server["interface"])
            except Exception as e:
                print(f"Error on {server['name']}: {e}")
                send_discord_notification(f"⚠️ Gagal mengecek status WireGuard pada {server['name']}: {e}")
        elif server["type"] == "debian-ssh":
            debian_ssh = DebianSSH(server, db)
            try:
                debian_ssh.check_status()
            except Exception as e:
                print(f"Error on {server['name']} ({server['host']}): {e}")
                send_discord_notification(f"⚠️ Gagal mengecek status WireGuard pada {server['name']} ({server['host']}): {e}")
        elif server["type"] == "mikrotik":
            from mikrotik import Mikrotik
            mikrotik = Mikrotik(server)
            mikrotik.ssh_connect()
            try:
                # Dapatkan status WireGuard dari MikroTik
                status_output = mikrotik.get_wireguard_status()

                # Filter peers berdasarkan interface
                filtered_peers = [peer for peer in status_output if peer.get("interface") == server["interface"]]

                # Format hasil
                formatted_status = "\n".join(
                    [f"Peer: {peer['name']}, Public Key: {peer['public-key']}, Allowed IP: {peer['allowed-address']}" for peer in filtered_peers]
                )

                print("WireGuard Status:\n", formatted_status)

                # Dapatkan total peers dari MikroTik
                total_peers = mikrotik.get_total_peers(server["interface"])
                print(f"Total Peers: {total_peers}")

                # Kirim notifikasi ke Discord jika webhook diatur
                send_discord_notification(f"WireGuard Status pada {server['name']} ({server['host']}):\n```{formatted_status}```\nTotal Peers: {total_peers}")

            except Exception as e:
                print(f"Error on {server['name']} ({server['host']}): {e}")
                send_discord_notification(f"⚠️ Gagal mengecek status WireGuard pada {server['name']} ({server['host']}): {e}")
            finally:
                mikrotik.ssh_close()