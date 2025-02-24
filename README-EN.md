# WireGuard Sync Manager

WireGuard Sync Manager is a tool for synchronizing and checking the status of WireGuard on Debian and MikroTik servers. This tool supports automatic synchronization using cron jobs and notifications to Discord.
## Features

- WireGuard synchronization on Debian (native and SSH) and MikroTik servers.
- WireGuard status checking.
- Sending notifications to Discord.
- Automatic synchronization using cron jobs.
- Automatic creation of `wg.conf` on Debian servers if not found.

## Project Structure

- `main.py`: Primary file for running WireGuard Sync Manager.
- `peer.py`: Manages Synchronizaztion and WireGuard status checking.
- `linux/debian_native.py`: Manages WireGuard on Debian server using native commands.
- `linux/debian_ssh.py`: Manages Wireguard on Debian servers through SSH.
- `mikrotik.py`: Manages Wireguard on MikroTik servers through SSH.
- `pgsql.py`: Fetches peers data from PostgreSQL database.
- `utils.py`: Sends notification to Discord.
- `config.json`: Configuration file for WireGuard Sync Manager.
- `example-config.json`: Example Configuration file for WireGuard Sync Manager.
- `requirements.txt`: Python Dependency List.
- `.github/dependabot.yml`: Dependabot configuration for dependency updates.
- `.gitignore`: List of files and directories to be ignored by Git.

## Installation

1. Clone this repository:
    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2. Create and activate a virtual environment (venv):
    ```sh
    python -m venv venv
    source venv/bin/activate  # Untuk Linux/MacOS
    .\venv\Scripts\activate  # Untuk Windows
    ```

3. Install Dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Copy example-config.json to config.json and modify it as needed:
    ```sh
    cp example-config.json config.json
    ```

5. Create PostgreSQL Database:
    ```sh
    sudo -u postgres psql
    CREATE DATABASE wg;
    CREATE USER wg WITH ENCRYPTED PASSWORD '1234';
    GRANT ALL PRIVILEGES ON DATABASE wg TO wg;
    \q
    ```

6. Create `wireguard_peers` table in PostgreSQL:
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

## Usage

Run `main.py` to start WireGuard Sync Manager:
```sh
python main.py
```

You will see the following menu:
```
=== WireGuard Sync Manager ===
1️⃣  Sinkronisasi Sekarang
2️⃣  Cek Status WireGuard
3️⃣  Toggle Cron Job (ON/OFF)
4️⃣  Periksa dan Buat wg.conf di Debian
5️⃣  Keluar
```

Select the desired option by entering its number.

## Configuration

### config.json

Here is an example of the config.json configuration:

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

###Explanation of the configuration

- `discord_webhook`: URL webhook Discord for sending notifications.
- `database`: Configuration for connecting to PostgreSQL database.
- `servers`: List of servers to be synchronized and have their status checked.
  - `type`: Server type (`debian-native`, `debian-ssh`, or mikrotik).
  - `name`: Server Name.
  - `host`: Address / FQDN of server (only for `debian-ssh` and mikrotik).
  - `port`: Port of SSH server (only for `debian-ssh` and mikrotik).
  - `user`: Username of SSH server (only for `debian-ssh` dan mikrotik).
  - `password`: Password of SSH server (only for `debian-ssh` dan mikrotik).
  - `interface`: Name of the WireGuard interface.
- `cron`: Cron job settings for automatic synchronization.
  - `enabled`: Enable or Disable cron job.
  - `interval_minutes`: Time interval for automatic synchronization (In minutes).

## Development

### Running Tests

For running tests, use the commans below:
```sh
pytest
```

### Adding Dependencies

To add a new dependency, add it to requirements.txt and run the following command:
```sh
pip install -r requirements.txt
```

### Using Dependabot

Dependabot is used to update dependencies automatically. It's configuration file is `dependabot.yml`
