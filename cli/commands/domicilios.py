"""
CLI Commands Domicilios
"""

import csv
from pathlib import Path

from rich.console import Console
from typer import Typer

from pjecz_casiopea_flask.blueprints.domicilios.models import Domicilio
from pjecz_casiopea_flask.lib.safe_string import safe_clave, safe_string
from pjecz_casiopea_flask.main import app

DOMICILIOS_CSV = "seed/domicilios.csv"

app.app_context().push()

domicilios = Typer()


@domicilios.command()
def alimentar():
    """Alimentar la base de datos con domicilios iniciales"""
    console = Console()
    console.print("Alimentando la base de datos con domicilios iniciales...")

    # Verificar que exista el archivo CSV
    ruta = Path(DOMICILIOS_CSV)
    if not ruta.is_file():
        console.print(f"[red]El archivo {DOMICILIOS_CSV} no existe.[/red]")
        return

    # Leer el archivo CSV e insertar
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        for renglon in csv.DictReader(puntero):
            clave = safe_clave(renglon.get("clave"))
            edificio = safe_string(renglon.get("edificio"), save_enie=True)
            estado = safe_string(renglon.get("estado"), save_enie=True)
            municipio = safe_string(renglon.get("municipio"), save_enie=True)
            calle = safe_string(renglon.get("calle"), save_enie=True)
            num_ext = safe_string(renglon.get("num_ext"))
            num_int = safe_string(renglon.get("num_int"))
            colonia = safe_string(renglon.get("colonia"), save_enie=True)
            cp = int(renglon.get("cp", "0"))
            es_activo = renglon.get("es_activo") == "1"
            estatus = renglon.get("estatus")
            domicilio = Domicilio(
                clave=clave,
                edificio=edificio,
                estado=estado,
                municipio=municipio,
                calle=calle,
                num_ext=num_ext,
                num_int=num_int,
                colonia=colonia,
                cp=cp,
                es_activo=es_activo,
                completo="",
                estatus=estatus,
            )
            domicilio.completo = domicilio.elaborar_completo()
            domicilio.save()
            contador += 1

    # Mensaje de éxito
    console.print(f"  [green]{contador} domicilios alimentados.[/green]")
