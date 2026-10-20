"""Demostracion del patron SINGLETON en los 6 microservicios.

Para cada servicio (con su propio entorno virtual) comprueba que:
  1. get_settings() y Settings.obtener_instancia() devuelven el MISMO objeto.
  2. Aun pidiendo la instancia desde 50 hilos a la vez (con la instancia
     reiniciada), solo se crea UNA (gracias al candado + doble verificacion).

Uso (desde la raiz del repositorio):
    python scripts/demo_singleton.py
"""

import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SERVICIOS = [
    "fleet-management-service",
    "vehicle-tracking-service",
    "route-optimization-service",
    "predictive-maintenance-service",
    "navigation-integration-service",
    "api-gateway",
]

CODIGO_EN_EL_SERVICIO = """
import json, threading
from app.core.config import Settings, get_settings

a = get_settings()
b = Settings.obtener_instancia()
c = get_settings()

Settings._instancia = None
ids, barrera = [], threading.Barrier(50)
def pedir():
    barrera.wait()
    ids.append(id(Settings.obtener_instancia()))
hilos = [threading.Thread(target=pedir) for _ in range(50)]
[h.start() for h in hilos]
[h.join() for h in hilos]

print(json.dumps({
    "app_name": a.app_name,
    "misma": a is b is c,
    "id": hex(id(a)),
    "instancias_en_50_hilos": len(set(ids)),
}))
"""


def python_del_servicio(servicio: Path) -> str:
    candidatos = [servicio / ".venv" / "Scripts" / "python.exe", servicio / ".venv" / "bin" / "python"]
    return str(next((c for c in candidatos if c.exists()), Path(sys.executable)))


def main() -> None:
    print("PATRON SINGLETON -- Settings.obtener_instancia() en cada microservicio\n")
    print(f"{'SERVICIO':<34}{'get_settings() is obtener_instancia()':<40}{'INSTANCIAS CREADAS CON 50 HILOS'}")
    print("-" * 110)
    todo_ok = True
    for nombre in SERVICIOS:
        carpeta = RAIZ / "services" / nombre
        salida = subprocess.run(
            [python_del_servicio(carpeta), "-c", CODIGO_EN_EL_SERVICIO],
            cwd=carpeta, capture_output=True, text=True,
        )
        if salida.returncode != 0:
            print(f"{nombre:<34}ERROR: {salida.stderr.strip().splitlines()[-1]}")
            todo_ok = False
            continue
        datos = json.loads(salida.stdout.strip().splitlines()[-1])
        ok = datos["misma"] and datos["instancias_en_50_hilos"] == 1
        todo_ok &= ok
        print(f"{nombre:<34}{'True  (id ' + datos['id'] + ')':<40}{datos['instancias_en_50_hilos']}  {'OK' if ok else 'FALLO'}")
    print("-" * 110)
    print("RESULTADO:", "los 6 servicios cumplen el Singleton" if todo_ok else "HAY SERVICIOS QUE NO LO CUMPLEN")


if __name__ == "__main__":
    main()
