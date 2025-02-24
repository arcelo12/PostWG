# filepath: /Users/florentinuskev/Desktop/Projects/WG-Sync/linux/debian_native.py
import subprocess

class DebianNative:
    def __init__(self, interface, db=None, utils=None):
        self.interface = interface
        self.db = db
        self.utils = utils

    def get_wireguard_status(self):
        """Mengambil status WireGuard menggunakan perintah native"""
        try:
            result = subprocess.run(
                ["wg", "show", self.interface, "dump"],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                raise Exception("Gagal mendapatkan status WireGuard.")

            # Parsing hasil untuk mendapatkan atribut name, public-key, dan allowed-address
            wg_peers = []
            for line in result.stdout.strip().split("\n")[1:]:
                fields = line.split()
                peer_info = {
                    "public-key": fields[0],
                    "allowed-address": fields[3],
                    "name": fields[4] if len(fields) > 4 else ""
                }
                wg_peers.append(peer_info)

            return wg_peers

        except Exception as e:
            raise Exception(f"Gagal mendapatkan status WireGuard: {e}")

    def add_wireguard_peer(self, name, public_key, allowed_ip):
        """Menambahkan peer WireGuard menggunakan perintah native"""
        try:
            subprocess.run(
                ["wg", "set", self.interface, "peer", public_key, "allowed-ips", allowed_ip],
                check=True
            )
            print(f"✅ Peer WireGuard {name} berhasil ditambahkan.")
        except subprocess.CalledProcessError as e:
            raise Exception(f"Gagal menambahkan peer WireGuard: {e}")

    def delete_wireguard_peer(self, public_key):
        """Menghapus peer WireGuard menggunakan perintah native"""
        try:
            subprocess.run(
                ["wg", "set", self.interface, "peer", public_key, "remove"],
                check=True
            )
            print(f"✅ Peer WireGuard dengan public-key {public_key} berhasil dihapus.")
        except subprocess.CalledProcessError as e:
            raise Exception(f"Gagal menghapus peer WireGuard: {e}")

    def sync_wireguard(self):
        try:
            # Ambil data dari database
            db_peers = self.db.get_peers()

            # Ambil daftar peer yang ada di WireGuard
            wg_peers = self.get_wireguard_status()
            wg_peer_keys = {peer["public-key"] for peer in wg_peers}

            # Sinkronisasi: Tambah peer baru, hapus peer lama
            db_peer_keys = {peer[1] for peer in db_peers}  # Menggunakan public_key sebagai kunci

            # Tambah peer yang belum ada di WireGuard
            for name, public_key, allowed_ip in db_peers:
                if public_key not in wg_peer_keys:
                    self.add_wireguard_peer(name, public_key, allowed_ip)

            # Hapus peer yang tidak ada di database
            for peer in wg_peers:
                if peer["public-key"] not in db_peer_keys:
                    self.delete_wireguard_peer(peer["public-key"])

            # Kirim notifikasi
            self.utils.send_discord_notification("✅ Sinkronisasi WireGuard selesai.")

        except Exception as e:
            print(f"Error: {e}")
            self.utils.send_discord_notification(f"⚠️ Gagal melakukan sinkronisasi WireGuard: {e}")

    def check_status(self):
        try:
            # Dapatkan status WireGuard
            status_output = self.get_wireguard_status()

            # Format hasil
            formatted_status = "\n".join(
            [f"Peer: {peer['name']}, Public Key: {peer['public-key']}, Allowed IP: {peer['allowed-address']}" for peer in status_output]
            )

            print("WireGuard Status:\n", formatted_status)

            # Kirim notifikasi ke Discord jika webhook diatur
            self.utils.send_discord_notification(f"WireGuard Status:\n```{formatted_status}```")

        except Exception as e:
            print(f"Error: {e}")
            self.utils.send_discord_notification(f"⚠️ Gagal mengecek status WireGuard: {e}")