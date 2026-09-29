# Conectar por TCP con los candidatos de la clase 1 y
# guardar el resultado de cada intento.

# cuando corre por primera vez se crea peers.json, si ya existe le da prioridad a connexiones ok 

# mock Addrman / gestión de direcciones


import socket
import json
from datetime import datetime, timezone
from pathlib import Path

SEEDS = [
    "seed.bitcoin.sipa.be",
    "dnsseed.bluematt.me",
    "seed.bitcoin.sprovoost.nl",
]

FILE = Path("peers.json")
PORT = 8333
TIMEOUT = 5
MAX_PEERS = 20


def save(peers):
    FILE.write_text(json.dumps(peers, indent=4))


def load():
    if FILE.exists():
        return json.loads(FILE.read_text())
    return []


def discover():
    """Obtener candidatos desde las DNS Seeds."""
    peers = []
    seen = set()

    for seed in SEEDS:
        try:
            results = socket.getaddrinfo(
                seed, PORT, type=socket.SOCK_STREAM
            )
        except socket.gaierror:
            continue

        for family, _, _, _, address in results:
            ip = address[0]

            if family not in (socket.AF_INET, socket.AF_INET6):
                continue

            if (ip, PORT) in seen:
                continue

            seen.add((ip, PORT))

            peers.append({
                "ip": ip,
                "port": PORT,
                "family": "IPv4" if family == socket.AF_INET else "IPv6",
                "source": seed,
                "last_attempt": None,
                "status": "new",
                "failures": 0
            })

    return peers


def connect(peer):
    """Intentar una conexión TCP al candidato."""
    family = (
        socket.AF_INET if peer["family"] == "IPv4"
        else socket.AF_INET6
    )

    try:
        with socket.socket(family, socket.SOCK_STREAM) as sock:
            sock.settimeout(TIMEOUT)
            sock.connect((peer["ip"], peer["port"]))

        status = "ok"

    except socket.timeout:
        status = "timeout"

    except ConnectionRefusedError:
        status = "refused"

    except OSError:
        status = "error"

    peer["last_attempt"] = datetime.now(timezone.utc).isoformat()
    peer["status"] = status

    if status == "ok":
        peer["failures"] = 0
    else:
        peer["failures"] += 1

    return status


def main():
    peers = load()

    if not peers:
        print("Consultando DNS Seeds...")
        peers = discover()
        save(peers) # Guardar en JSON 
    else:
        print("Cargando candidatos desde peers.json...")

    # Priorizar los que respondieron anteriormente
    peers.sort(key=lambda p: p["status"] != "ok")

    attempts = 0

    for peer in peers:
        if peer["failures"] >= 3:
            continue

        if attempts >= MAX_PEERS:
            break

        status = connect(peer)
        attempts += 1

        print(f'{peer["ip"]:42} {peer["family"]} -> {status}')

        # Persistir cada intento inmediatamente
        save(peers)

    print(f"\nIntentos realizados: {attempts}")


if __name__ == "__main__":
    main()
