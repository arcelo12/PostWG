import json
import os
from mikrotik.login import connect_ssh

# Load konfigurasi
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_path = os.path.join(base_dir, "config.json")

with open(config_path, "r") as f:
    config = json.load(f)

MIKROTIK_CONFIG = config["mikrotik"]

def get_wireguard_status():
    """Mengambil status WireGuard dari MikroTik melalui SSH"""
    ssh = connect_ssh()

    try:
        command = f'/interface/wireguard/peers/print terse'
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode().strip()

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
    except Exception as e:
        raise Exception(f"Gagal menghubungkan ke MikroTik: {e}")
    finally:
        ssh.close()

def get_total_peers(interface):
    """Mengambil total jumlah peers dari MikroTik melalui SSH untuk interface tertentu"""
    ssh = connect_ssh()

    try:
        command = f'/interface/wireguard/peers/print terse where interface={interface}'
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode().strip()

        if not output:
            raise Exception("Gagal mendapatkan total peers dari MikroTik.")

        # Hitung total peers yang tidak memiliki tanda 'X'
        total_peers = sum(1 for line in output.split("\n") if 'X' not in line)

        print(f"Total Peers: {total_peers}")
        return total_peers
    except Exception as e:
        raise Exception(f"Gagal menghubungkan ke MikroTik: {e}")
    finally:
        ssh.close()