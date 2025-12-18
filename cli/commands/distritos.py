"""
CLI Commands Distritos
"""

import csv
from pathlib import Path

from rich.console import Console
from typer import Typer

from pjecz_casiopea_flask.blueprints.distritos.models import Distrito
from pjecz_casiopea_flask.lib.safe_string import safe_clave, safe_string
from pjecz_casiopea_flask.main import app

DISTRITOS_CSV = "seed/distritos.csv"

app.app_context().push()

distritos = Typer()


@distritos.command()
def alimentar():
    """Alimentar la base de datos con distritos iniciales"""
    console = Console()
    console.print("Alimentando la base de datos con distritos iniciales...")

    # Verificar que exista el archivo CSV
    ruta = Path(DISTRITOS_CSV)
    if not ruta.is_file():
        console.print(f"[red]El archivo {DISTRITOS_CSV} no existe.[/red]")
        return

    # Leer el archivo CSV e insertar
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        for renglon in csv.DictReader(puntero):
            clave = safe_clave(renglon.get("clave"))
            nombre = safe_string(renglon.get("nombre"), save_enie=True)
            nombre_corto = safe_string(renglon.get("nombre_corto"), save_enie=True)
            es_activo = renglon.get("es_activo") == "1"
            es_distrito_judicial = renglon.get("es_distrito_judicial") == "1"
            es_distrito = renglon.get("es_distrito_judicial") == "1"
            es_jurisdiccional = renglon.get("es_distrito_judicial") == "1"
            estatus = renglon.get("estatus")
            distrito = Distrito(
                clave=clave,
                nombre=nombre,
                nombre_corto=nombre_corto,
                es_activo=es_activo,
                es_distrito_judicial=es_distrito_judicial,
                es_distrito=es_distrito,
                es_jurisdiccional=es_jurisdiccional,
                estatus=estatus,
            )
            distrito.save()
            contador += 1

    # Mensaje de éxito
    console.print(f"  [green]{contador} distritos alimentados.[/green]")
