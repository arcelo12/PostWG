# WireGuard Sync Manager

WireGuard Sync Manager adalah alat untuk sinkronisasi dan pengecekan status WireGuard pada server Debian dan MikroTik. Alat ini mendukung sinkronisasi otomatis menggunakan cron job dan notifikasi ke Discord.

## Fitur

- Sinkronisasi WireGuard pada server Debian (native dan SSH) dan MikroTik.
- Pengecekan status WireGuard.
- Notifikasi ke Discord.
- Sinkronisasi otomatis menggunakan cron job.
- Pembuatan file `wg.conf` pada server Debian jika belum ada.

## Struktur Proyek

- `main.py`: File utama untuk menjalankan WireGuard Sync Manager.
- `peer.py`: Mengelola sinkronisasi dan pengecekan status WireGuard.
- `linux/debian_native.py`: Mengelola WireGuard pada server Debian menggunakan perintah native.
- `linux/debian_ssh.py`: Mengelola WireGuard pada server Debian melalui SSH.
- `mikrotik.py`: Mengelola WireGuard pada server MikroTik melalui SSH.
- `pgsql.py`: Mengambil data peers dari database PostgreSQL.
- `utils.py`: Mengirim notifikasi ke Discord.
- `config.json`: Konfigurasi untuk WireGuard Sync Manager.
- `example-config.json`: Contoh konfigurasi untuk WireGuard Sync Manager.
- `requirements.txt`: Daftar dependensi Python.
- `.github/dependabot.yml`: Pengaturan Dependabot untuk pembaruan dependensi.
- `.gitignore`: Daftar file dan direktori yang diabaikan oleh Git.

## Instalasi

1. Clone repositori ini:
    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2. Buat virtual environment dan aktifkan:
    ```sh
    python -m venv venv
    source venv/bin/activate  # Untuk Linux/MacOS
    .\venv\Scripts\activate  # Untuk Windows
    ```

3. Instal dependensi:
    ```sh
    pip install -r requirements.txt
    ```

4. Salin example-config.json menjadi config.json dan sesuaikan dengan kebutuhan Anda:
    ```sh
    cp example-config.json config.json
    ```

5. Buat database PostgreSQL:
    ```sh
    sudo -u postgres psql
    CREATE DATABASE wg;
    CREATE USER wg WITH ENCRYPTED PASSWORD '1234';
    GRANT ALL PRIVILEGES ON DATABASE wg TO wg;
    \q
    ```

6. Buat tabel `wireguard_peers` di PostgreSQL:
    ```sh
    sudo -u postgres psql -d wg
    CREATE TABLE IF NOT EXISTS public.wireguard_peers (
        id integer NOT NULL DEFAULT nextval('wireguard_peers_id_seq'::regclass),
        name character varying(255) NOT NULL,
        public_key text NOT NULL,
        allowed_ip text NOT NULL,
        created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT wireguard_peers_pkey PRIMARY KEY (id),
        CONSTRAINT wireguard_peers_name_key UNIQUE (name)
    );
    \q
    ```

## Penggunaan

Jalankan `main.py` untuk memulai WireGuard Sync Manager:
```sh
python main.py
```

Anda akan melihat menu berikut:
```
=== WireGuard Sync Manager ===
1️⃣  Sinkronisasi Sekarang
2️⃣  Cek Status WireGuard
3️⃣  Toggle Cron Job (ON/OFF)
4️⃣  Periksa dan Buat wg.conf di Debian
5️⃣  Keluar
```

Pilih opsi yang diinginkan dengan memasukkan nomor opsi.

## Konfigurasi

### config.json

Berikut adalah contoh konfigurasi config.json:

```json
{
    "discord_webhook": "https://discord.com/api/webhooks/<WEBHOOK-ID>",
    "database": {
        "host": "127.0.0.1",
        "port": 5432,
        "user": "wg",
        "password": "1234",
        "dbname": "wg"
    },
    "servers": [
        {
            "type": "debian-native",
            "name": "Server-A",
            "interface": "wireguard"
        },
        {
            "type": "mikrotik",
            "name": "Server-B",
            "host": "127.0.0.1",
            "port": 22,
            "user": "user",
            "password": "password",
            "interface": "wireguard"
        },
        {
            "type": "debian-ssh",
            "name": "Debian-Server-1",
            "host": "127.0.0.1",
            "port": 22,
            "user": "root",
            "password": "password",
            "interface": "wg0"
        }
    ],
    "cron": {
        "enabled": false,
        "interval_minutes": 5
    }
}
```

### Penjelasan Konfigurasi

- `discord_webhook`: URL webhook Discord untuk mengirim notifikasi.
- `database`: Konfigurasi koneksi ke database PostgreSQL.
- `servers`: Daftar server yang akan disinkronisasi dan dicek statusnya.
  - `type`: Jenis server (`debian-native`, `debian-ssh`, atau mikrotik).
  - `name`: Nama server.
  - `host`: Alamat host server (hanya untuk `debian-ssh` dan mikrotik).
  - `port`: Port SSH server (hanya untuk `debian-ssh` dan mikrotik).
  - `user`: Username SSH server (hanya untuk `debian-ssh` dan mikrotik).
  - `password`: Password SSH server (hanya untuk `debian-ssh` dan mikrotik).
  - `interface`: Nama interface WireGuard.
- `cron`: Pengaturan cron job untuk sinkronisasi otomatis.
  - `enabled`: Mengaktifkan atau menonaktifkan cron job.
  - `interval_minutes`: Interval waktu sinkronisasi otomatis dalam menit.

## Pengembangan

### Menjalankan Tes

Untuk menjalankan tes, gunakan perintah berikut:
```sh
pytest
```

### Menambahkan Dependensi

Untuk menambahkan dependensi baru, tambahkan ke requirements.txt dan jalankan perintah berikut:
```sh
pip install -r requirements.txt
```

### Menggunakan Dependabot

Dependabot digunakan untuk memperbarui dependensi secara otomatis. Pengaturan Dependabot terdapat di `dependabot.yml`.
