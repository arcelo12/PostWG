import paramiko
from utils import Utils

class DebianSSH:
    def __init__(self, ssh_config, db):
        self.ssh_config = ssh_config
        self.db = db
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.connected = False

    def ssh_connect(self):
        """Membuat koneksi SSH ke Debian"""
        if not self.connected:
            try:
                print(f"🔄 Menghubungkan ke Debian {self.ssh_config['host']}:{self.ssh_config['port']}...")
                self.ssh.connect(
                    hostname=self.ssh_config["host"],
                    port=self.ssh_config["port"],
                    username=self.ssh_config["user"],
                    password=self.ssh_config["password"]
                )
                self.connected = True
                print("✅ Koneksi SSH berhasil!")
            except Exception as e:
                print(f"❌ Gagal menghubungkan ke Debian: {e}")
                raise e

    def execute_command(self, command):
        """Menjalankan perintah di Debian melalui SSH"""
        if not self.connected:
            self.ssh_connect()
        stdin, stdout, stderr = self.ssh.exec_command(command)
        return stdout.read().decode().strip()

    def ssh_close(self):
        """Menutup koneksi SSH"""
        if self.connected:
            self.ssh.close()
            self.connected = False
            print("🔒 Koneksi SSH ditutup.")

    def add_wireguard_peer(self, name, public_key, allowed_ip, interface):
        """Menambahkan peer WireGuard ke Debian melalui SSH"""
        command = f'wg set {interface} peer {public_key} allowed-ips {allowed_ip}'
        self.execute_command(command)

    def delete_wireguard_peer(self, public_key, interface):
        """Menghapus peer WireGuard dari Debian melalui SSH"""
        command = f'wg set {interface} peer {public_key} remove'
        self.execute_command(command)

    def get_wireguard_status(self):
        """Mengambil status WireGuard dari Debian melalui SSH"""
        command = f'wg show {self.ssh_config["interface"]} dump'
        output = self.execute_command(command)

        if not output:
            raise Exception("Gagal mendapatkan status WireGuard dari Debian.")

        # Parsing hasil untuk mendapatkan atribut name, public-key, dan allowed-address
        wg_peers = []
        for line in output.split("\n")[1:]:
            fields = line.split()
            peer_info = {
                "public-key": fields[0],
                "allowed-address": fields[3],
                "name": fields[4] if len(fields) > 4 else ""
            }
            wg_peers.append(peer_info)

        return wg_peers

    def sync_wireguard(self):
        try:
            # Ambil data dari database
            db_peers = self.db.get_peers()

            # Ambil daftar peer yang ada di WireGuard
            wg_peers = self.get_wireguard_status()
            wg_peer_keys = {(peer["public-key"], peer["name"]) for peer in wg_peers}

            # Sinkronisasi: Tambah peer baru, hapus peer lama
            db_peer_keys = {(peer[1], peer[0]) for peer in db_peers}  # Menggunakan name sebagai kunci

            # Tambah peer yang belum ada di WireGuard
            for name, public_key, allowed_ip in db_peers:
                if (public_key, name) not in wg_peer_keys:
                    self.add_wireguard_peer(name, public_key, allowed_ip, self.ssh_config["interface"])

            # Hapus peer yang tidak ada di database
            for peer in wg_peers:
                if (peer["public-key"], peer["name"]) not in db_peer_keys:
                    self.delete_wireguard_peer(peer["public-key"], self.ssh_config["interface"])

            # Kirim notifikasi
            Utils.send_discord_notification(f"✅ Sinkronisasi WireGuard selesai pada {self.ssh_config['host']}.")
        except KeyError as e:
            print(f"Error: Missing configuration key: {e}")
            Utils.send_discord_notification(f"⚠️ Gagal melakukan sinkronisasi WireGuard pada {self.ssh_config.get('host', 'unknown')}: Missing configuration key: {e}")
        except Exception as e:
            print(f"Error: {e}")
            Utils.send_discord_notification(f"⚠️ Gagal melakukan sinkronisasi WireGuard pada {self.ssh_config.get('host', 'unknown')}: {e}")
        finally:
            self.ssh_close()

    def check_status(self):
        try:
            # Dapatkan status WireGuard dari Debian
            status_output = self.get_wireguard_status()

            # Format hasil
            formatted_status = "\n".join(
                [f"Peer: {peer['name']}, Public Key: {peer['public-key']}, Allowed IP: {peer['allowed-address']}" for peer in status_output]
            )

            print("WireGuard Status:\n", formatted_status)

            # Kirim notifikasi ke Discord jika webhook diatur
            Utils.send_discord_notification(f"WireGuard Status pada {self.ssh_config['host']}:\n```{formatted_status}```")

        except KeyError as e:
            print(f"Error: Missing configuration key: {e}")
            Utils.send_discord_notification(f"⚠️ Gagal mengecek status WireGuard pada {self.ssh_config.get('host', 'unknown')}: Missing configuration key: {e}")
        except Exception as e:
            print(f"Error: {e}")
            Utils.send_discord_notification(f"⚠️ Gagal mengecek status WireGuard pada {self.ssh_config.get('host', 'unknown')}: {e}")
        finally:
            self.ssh_close()