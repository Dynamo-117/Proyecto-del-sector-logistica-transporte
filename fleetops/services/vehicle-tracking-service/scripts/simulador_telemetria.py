"""Simulador de telemetria: envia lecturas aleatorias de posicion/velocidad
para un vehiculo ya conocido por el servicio, a intervalos regulares.

Uso:
    python scripts/simulador_telemetria.py <vehiculo_id> [--url http://localhost:8002] [--intervalo 2]
"""

import argparse
import random
import time

import httpx

LAT_BASE, LON_BASE = 4.7110, -74.0721  # Bogota, como punto de partida


def generar_lectura() -> dict:
    return {
        "latitud": LAT_BASE + random.uniform(-0.01, 0.01),
        "longitud": LON_BASE + random.uniform(-0.01, 0.01),
        "velocidad_kmh": max(0.0, random.gauss(40, 15)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("vehiculo_id", help="UUID del vehiculo, ya conocido por el servicio")
    parser.add_argument("--url", default="http://localhost:8002", help="Base URL del servicio")
    parser.add_argument("--intervalo", type=float, default=2.0, help="Segundos entre lecturas")
    parser.add_argument("--iteraciones", type=int, default=0, help="0 = infinito")
    args = parser.parse_args()

    contador = 0
    with httpx.Client(base_url=args.url, timeout=5.0) as client:
        while args.iteraciones == 0 or contador < args.iteraciones:
            lectura = generar_lectura() | {"vehiculo_id": args.vehiculo_id}
            respuesta = client.post("/telemetria", json=lectura)
            print(respuesta.status_code, respuesta.json())
            contador += 1
            time.sleep(args.intervalo)


if __name__ == "__main__":
    main()
