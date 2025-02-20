import psycopg2
import json
import os

# Load konfigurasi
base_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(base_dir, "config.json")

with open(config_path, "r") as f:
    config = json.load(f)

DB_CONFIG = config["database"]

def get_db_peers():
    """Mengambil data peers dari database PostgreSQL"""
    conn = psycopg2.connect(
        dbname=DB_CONFIG["dbname"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"]
    )
    cursor = conn.cursor()

    cursor.execute("SELECT name, public_key, allowed_ip FROM wireguard_peers")
    db_peers = cursor.fetchall()

    conn.close()
    return db_peers