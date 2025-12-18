"""
CLI Commands Modulos
"""

import csv
from pathlib import Path

from rich.console import Console
from typer import Typer

from pjecz_casiopea_flask.blueprints.modulos.models import Modulo
from pjecz_casiopea_flask.lib.safe_string import safe_string
from pjecz_casiopea_flask.main import app

MODULOS_CSV = "seed/modulos.csv"

app.app_context().push()

modulos = Typer()


@modulos.command()
def alimentar():
    """Alimentar la base de datos con modulos iniciales"""
    console = Console()
    console.print("Alimentando la base de datos con modulos iniciales...")

    # Verificar que exista el archivo CSV
    ruta = Path(MODULOS_CSV)
    if not ruta.is_file():
        console.print(f"[red]El archivo {MODULOS_CSV} no existe.[/red]")
        return

    # Leer el archivo CSV e insertar
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        for renglon in csv.DictReader(puntero):
            nombre = safe_string(renglon.get("nombre"), save_enie=True)
            nombre_corto = safe_string(renglon.get("nombre_corto"), do_unidecode=False, save_enie=True, to_uppercase=False)
            icono = renglon.get("icono")
            ruta = renglon.get("ruta")
            en_navegacion = renglon.get("en_navegacion") == "1"
            estatus = renglon.get("estatus")
            modulo = Modulo(
                nombre=nombre,
                nombre_corto=nombre_corto,
                icono=icono,
                ruta=ruta,
                en_navegacion=en_navegacion,
                estatus=estatus,
            )
            modulo.save()
            contador += 1

    # Mensaje de éxito
    console.print(f"  [green]{contador} módulos alimentados.[/green]")
