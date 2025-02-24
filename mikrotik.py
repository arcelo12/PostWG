import paramiko
import time

class Mikrotik:
    def __init__(self, mikrotik_config):
        self.name = mikrotik_config["name"]
        self.mikrotik_config = mikrotik_config
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.connected = False

    def ssh_connect(self, retries=3, delay=5):
        """Membuat koneksi SSH ke MikroTik dengan mekanisme retry"""
        attempt = 0
        while attempt < retries:
            try:
                print(f"🔄 Menghubungkan ke {self.name} ({self.mikrotik_config['host']}:{self.mikrotik_config['port']})... (Percobaan {attempt + 1})")
                self.ssh.connect(
                    hostname=self.mikrotik_config["host"],
                    port=self.mikrotik_config["port"],
                    username=self.mikrotik_config["user"],
                    password=self.mikrotik_config["password"],
                    timeout=30  # Tambahkan timeout yang lebih lama
                )
                self.connected = True
                print(f"✅ Koneksi SSH ke {self.name} berhasil!")
                return
            except Exception as e:
                print(f"❌ Gagal menghubungkan ke {self.name}: {e}")
                attempt += 1
                if attempt < retries:
                    print(f"🔄 Mencoba kembali dalam {delay} detik...")
                    time.sleep(delay)
                else:
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
    
    def sync_wireguard(self, db_peers):
        wg_peers = self.get_wireguard_status()
        wg_peer_keys = {(peer["public-key"], peer["name"]) for peer in wg_peers}
        db_peer_keys = {(peer[1], peer[0]) for peer in db_peers}

        for name, public_key, allowed_ip in db_peers:
            if (public_key, name) not in wg_peer_keys:
                self.add_wireguard_peer(name, public_key, allowed_ip, self.server["interface"])

        for peer in wg_peers:
            if (peer["public-key"], peer["name"]) not in db_peer_keys:
                self.delete_wireguard_peer(peer["public-key"], peer["name"], self.server["interface"])

    def check_wireguard_status(self):
        status_output = self.get_wireguard_status()
        filtered_peers = [peer for peer in status_output if peer.get("interface") == self.server["interface"]]
        formatted_status = "\n".join(
            [f"Peer: {peer['name']}, Public Key: {peer['public-key']}, Allowed IP: {peer['allowed-address']}" for peer in filtered_peers]
        )
        print("WireGuard Status:\n", formatted_status)
        total_peers = self.get_total_peers(self.server["interface"])
        print(f"Total Peers: {total_peers}")
        return formatted_status, total_peers