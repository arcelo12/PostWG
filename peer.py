from linux.debian_ssh import DebianSSH
from linux.debian_native import DebianNative
from mikrotik import Mikrotik

def sync_wireguard(config, db, utils):
    db_peers = db.get_peers()  # Fetch database peers once

    for server in config["servers"]:
        try:
            if server["type"] == "debian-native":
                debian_native = DebianNative(server["interface"], db, utils)
                debian_native.sync_wireguard()
            elif server["type"] == "debian-ssh":
                with DebianSSH(server, db) as debian_ssh:
                    debian_ssh.sync_wireguard()
            elif server["type"] == "mikrotik":
                with Mikrotik(server) as mikrotik:
                    mikrotik.sync_wireguard(db_peers)
            utils.send_discord_notification(f"✅ Sinkronisasi WireGuard selesai pada {server['name']} ({server['host']}).")
        except Exception as e:
            print(f"Error on {server['name']} ({server['host']}): {e}")
            utils.send_discord_notification(f"⚠️ Gagal melakukan sinkronisasi WireGuard pada {server['name']} ({server['host']}): {e}")

def check_status(config, db, utils):
    for server in config["servers"]:
        try:
            if server["type"] == "debian-native":
                debian_native = DebianNative(server["interface"], utils=utils)
                debian_native.check_status()
            elif server["type"] == "debian-ssh":
                with DebianSSH(server, db) as debian_ssh:
                    debian_ssh.check_status()
            elif server["type"] == "mikrotik":
                with Mikrotik(server) as mikrotik:
                    formatted_status, total_peers = mikrotik.check_wireguard_status()
                    utils.send_discord_notification(f"WireGuard Status pada {server['name']} ({server['host']}):\n```{formatted_status}```\nTotal Peers: {total_peers}")
        except Exception as e:
            print(f"Error on {server['name']} ({server['host']}): {e}")
            utils.send_discord_notification(f"⚠️ Gagal mengecek status WireGuard pada {server['name']} ({server['host']}): {e}")