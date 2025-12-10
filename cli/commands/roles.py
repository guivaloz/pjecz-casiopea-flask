"""
CLI Commands Roles
"""

import csv
from pathlib import Path

from rich.console import Console
from typer import Typer

from pjecz_casiopea_flask.blueprints.roles.models import Rol
from pjecz_casiopea_flask.lib.safe_string import safe_string
from pjecz_casiopea_flask.main import app

ROLES_CSV = "seed/roles_permisos.csv"

app.app_context().push()

roles = Typer()


@roles.command()
def alimentar():
    """Alimentar la base de datos con roles iniciales"""
    console = Console()
    console.print("Alimentando la base de datos con roles iniciales...")

    # Verificar que exista el archivo CSV
    ruta = Path(ROLES_CSV)
    if not ruta.is_file():
        console.print(f"[red]El archivo {ROLES_CSV} no existe.[/red]")
        return

    # Leer el archivo CSV e insertar
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        for renglon in csv.DictReader(puntero):
            nombre = safe_string(renglon.get("rol_nombre"), save_enie=True)
            estatus = renglon.get("estatus")
            rol = Rol(
                nombre=nombre,
                estatus=estatus,
            )
            rol.save()
            contador += 1

    # Mensaje de éxito
    console.print(f"   [green]{contador} roles alimentados.[/green]")
