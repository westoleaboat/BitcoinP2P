# consultar las semillas con dig y leer la respuesta
# recorrer el código de Bitcoin Core donde se declaran las semillas y las direcciones embebidas
# programa que consulta las semillas y loguea las direcciones obtenidas


import socket

SEEDS = [ # https://github.com/bitcoin/bitcoin/blob/master/src/kernel/chainparams.cpp#L168
    "dnsseed.bluematt.me",              # Matt Corallo, only supports x9
    "seed.bitcoin.jonasschnelli.ch",    # Jonas Schnelli, only supports x1, x5, x9, and xd
    "seed.btc.petertodd.net",           # Peter Todd, only supports x1, x5, x9, and xd
    "seed.bitcoin.sprovoost.nl",        # Sjors Provoost       
    "dnsseed.emzy.de",                  # Stephan Oeste
    "seed.bitcoin.wiz.biz",             # Jason Maurice
    "seed.mainnet.achownodes.xyz",      # Ava Chow, only supports x1, x5, x9, x49, x809, x849, xd, x400, x404, x408, x448, xc08, xc48, x40c
]


def resolve(seed: str):
    """
    Resuelve la semilla y devuelve una lista de tuplas (ip, kind)
    """
    
    try:
        results = socket.getaddrinfo(
            seed,
            None,
            type=socket.SOCK_STREAM
        )
    except socket.gaierror as error:
        print(f"Error consultando {seed}: {error}")
        return []

    addresses = []

    for family, _, _, _, sockaddr in results:
        ip = sockaddr[0]

        kind = (
            "IPv4" if family == socket.AF_INET
            else "IPv6"
        )

        addresses.append((ip, kind))

    return list(set(addresses))


def main():
    """
    ejecuta resolve(seed) y muestra las direcciones ip con su tipo IPv4 o IPv6.
    enumera la cantidad de IPs unicas
    """
    all_addresses = set()

    for seed in SEEDS:
        print(f"\nConsultando: {seed}")

        addresses = resolve(seed)

        for ip, kind in addresses:
            print(f"  {ip:42} {kind}")
            all_addresses.add(ip)

        print(f"Direcciones obtenidas: {len(addresses)}")

    print("\n-------------------------")
    print(f"IPs únicas: {len(all_addresses)}")


if __name__ == "__main__":
    main()
