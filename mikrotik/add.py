import json
import os
from mikrotik.login import connect_ssh

# Load konfigurasi
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_path = os.path.join(base_dir, "config.json")

with open(config_path, "r") as f:
    config = json.load(f)

MIKROTIK_CONFIG = config["mikrotik"]

def add_wireguard_peer_to_mikrotik(name, public_key, allowed_ip, interface):
    """Menambahkan peer WireGuard ke MikroTik melalui SSH"""
    ssh = connect_ssh()

    try:
        command = f'/interface/wireguard/peers/add name={name} public-key="{public_key}" allowed-address={allowed_ip} interface={interface}'
        ssh.exec_command(command)
    except Exception as e:
        raise Exception(f"Gagal menambahkan peer ke MikroTik: {e}")
    finally:
        ssh.close()