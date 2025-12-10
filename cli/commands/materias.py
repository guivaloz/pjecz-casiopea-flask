"""
CLI Commands Materias
"""

import csv
from pathlib import Path

from rich.console import Console
from typer import Typer

from pjecz_casiopea_flask.blueprints.materias.models import Materia
from pjecz_casiopea_flask.lib.safe_string import safe_clave, safe_string
from pjecz_casiopea_flask.main import app

MATERIAS_CSV = "seed/materias.csv"

app.app_context().push()

materias = Typer()


@materias.command()
def alimentar():
    """Alimentar la base de datos con materias iniciales"""
    console = Console()
    console.print("Alimentando la base de datos con materias iniciales...")

    # Verificar que exista el archivo CSV
    ruta = Path(MATERIAS_CSV)
    if not ruta.is_file():
        console.print(f"[red]El archivo {MATERIAS_CSV} no existe.[/red]")
        return

    # Leer el archivo CSV e insertar
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        for renglon in csv.DictReader(puntero):
            clave = safe_clave(renglon.get("clave"))
            nombre = safe_string(renglon.get("nombre"), save_enie=True)
            descripcion = safe_string(renglon.get("descripcion"), save_enie=True)
            estatus = renglon.get("estatus")
            materia = Materia(
                clave=clave,
                nombre=nombre,
                descripcion=descripcion,
                estatus=estatus,
            )
            materia.save()
            contador += 1

    # Mensaje de éxito
    console.print(f"  [green]{contador} materias alimentadas.[/green]")
