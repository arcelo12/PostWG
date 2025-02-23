import psycopg2

def get_db_peers(DB_CONFIG):
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