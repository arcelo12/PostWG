from psycopg2 import pool

class DB:
    def __init__(self, db_conf):
        # Initialize Instance Variable
        self.pool = pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            dbname=db_conf["dbname"],
            user=db_conf["user"],
            password=db_conf["password"],
            host=db_conf["host"],
            port=db_conf["port"]
        )

    def get_peers(self):
        """Mengambil data peers dari database PostgreSQL"""
        # Get Connection from Pool
        conn = self.pool.getconn()

        try:
            with conn.cursor() as cursor:  
                cursor.execute("SELECT name, public_key, allowed_ip FROM wireguard_peers")
                db_peers = cursor.fetchall()
                print("[DB] Successfuly to fetch Wireguard Peers from Database...")
                return db_peers
        except:
            print("[DB] Failed to fetch Wireguard Peers from Database...")
        finally:
            self.pool.putconn(conn)  # Return the connection to the pool

    def add_peer(self):
        # Do something here...
        return None