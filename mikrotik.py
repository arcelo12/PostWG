import paramiko
import json
import os

# Load konfigurasi
base_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(base_dir, "config.json")

with open(config_path, "r") as f:
    config = json.load(f)


class Mikrotik:
    def __init__(self, mikrotik_config):
        self.name = mikrotik_config["name"]
        self.mikrotik_config = mikrotik_config
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.connected = False

    def ssh_connect(self):
        """Membuat koneksi SSH ke MikroTik"""
        if not self.connected:
            try:
                print(f"🔄 Menghubungkan ke {self.name} ({self.mikrotik_config['host']}:{self.mikrotik_config['port']})...")
                self.ssh.connect(
                    hostname=self.mikrotik_config["host"],
                    port=self.mikrotik_config["port"],
                    username=self.mikrotik_config["user"],
                    password=self.mikrotik_config["password"],
                    timeout=10  # Tambahkan timeout
                )
                self.connected = True
                print("✅ Koneksi SSH ke {self.name} berhasil!")
            except Exception as e:
                print(f"❌ Gagal menghubungkan ke {self.name}: {e}")
                raise e

    def execute_command(self, command):
        """Menjalankan perintah di MikroTik melalui SSH"""
        if not self.connected:
            self.ssh_connect()
        stdin, stdout, stderr = self.ssh.exec_command(command)
        return stdout.read().decode().strip()

    def ssh_close(self):
        """Menutup koneksi SSH"""
        if self.connected:
            self.ssh.close()
            self.connected = False
            print(f"🔒 Koneksi SSH ke {self.name} ditutup.")

    def add_wireguard_peer(self, name, public_key, allowed_ip, interface):
        """Menambahkan peer WireGuard ke MikroTik melalui SSH"""
        command = f'/interface/wireguard/peers/add name={name} public-key="{public_key}" allowed-address={allowed_ip} interface={interface}'
        self.execute_command(command)

    def delete_wireguard_peer(self, public_key, name, interface):
        """Menghapus peer WireGuard dari MikroTik melalui SSH"""
        command = f'/interface/wireguard/peers/remove [find public-key="{public_key}" && name={name} && interface={interface}]'
        self.execute_command(command)

    def get_wireguard_status(self):
        """Mengambil status WireGuard dari MikroTik melalui SSH"""
        command = f'/interface/wireguard/peers/print terse'
        output = self.execute_command(command)

        if not output:
            raise Exception("Gagal mendapatkan status WireGuard dari MikroTik.")

        # Parsing hasil untuk mendapatkan atribut name, public-key, dan allowed-address
        wg_peers = []
        for line in output.split("\n"):
            peer_info = {}
            for item in line.split(" "):
                if "=" in item:
                    key, value = item.split("=", 1)
                    if key in ["name", "public-key", "allowed-address", "interface"]:
                        peer_info[key] = value
            if peer_info:
                wg_peers.append(peer_info)

        return wg_peers

    def get_total_peers(self, interface):
        """Mengambil total jumlah peers dari MikroTik melalui SSH untuk interface tertentu"""
        command = f'/interface/wireguard/peers/print terse where interface={interface}'
        output = self.execute_command(command)

        if not output:
            raise Exception("Gagal mendapatkan total peers dari MikroTik.")

        # Hitung total peers yang tidak memiliki tanda 'X'
        total_peers = sum(1 for line in output.split("\n") if 'X' not in line)

        print(f"Total Peers: {total_peers}")
        return total_peers

def test_ssh_connection():
    """Menguji koneksi SSH ke MikroTik"""
    mikrotik = Mikrotik(config["mikrotik"][0])
    mikrotik.ssh_connect()
    mikrotik.ssh_close()

if __name__ == "__main__":
    test_ssh_connection()