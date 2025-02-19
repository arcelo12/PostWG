import paramiko
import json
import os

# Load konfigurasi
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_path = os.path.join(base_dir, "config.json")

with open(config_path, "r") as f:
    config = json.load(f)

MIKROTIK_CONFIG = config["mikrotik"]

def delete_wireguard_peer(public_key, name, interface):
    """Menghapus peer WireGuard dari MikroTik melalui SSH"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"🔄 Menghapus peer WireGuard dari MikroTik {MIKROTIK_CONFIG['host']}...")
        ssh.connect(
            hostname=MIKROTIK_CONFIG["host"],
            port=MIKROTIK_CONFIG["port"],
            username=MIKROTIK_CONFIG["user"],
            password=MIKROTIK_CONFIG["password"]
        )

        command = f'/interface/wireguard/peers/remove [find public-key="{public_key}" && name={name} && interface={interface}]'
        ssh.exec_command(command)

    except Exception as e:
        raise Exception(f"Gagal menghapus peer dari MikroTik: {e}")
    finally:
        ssh.close()