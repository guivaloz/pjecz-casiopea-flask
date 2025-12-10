"""
CLI Commands Autoridades
"""

import csv
from pathlib import Path

from rich.console import Console
from typer import Typer

from pjecz_casiopea_flask.blueprints.autoridades.models import Autoridad
from pjecz_casiopea_flask.blueprints.distritos.models import Distrito
from pjecz_casiopea_flask.blueprints.materias.models import Materia
from pjecz_casiopea_flask.lib.safe_string import safe_clave, safe_string
from pjecz_casiopea_flask.main import app

AUTORIDADES_CSV = "seed/autoridades.csv"

app.app_context().push()

autoridades = Typer()


@autoridades.command()
def alimentar():
    """Alimentar la base de datos con autoridades iniciales"""
    console = Console()
    console.print("Alimentando la base de datos con autoridades iniciales...")

    # Verificar que exista el archivo CSV
    ruta = Path(AUTORIDADES_CSV)
    if not ruta.is_file():
        console.print(f"[red]El archivo {AUTORIDADES_CSV} no existe.[/red]")
        return

    # Leer el archivo CSV e insertar
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        for renglon in csv.DictReader(puntero):
            distrito_clave = safe_clave(renglon.get("distrito_clave"))
            materia_clave = safe_clave(renglon.get("materia_clave"))
            clave = safe_clave(renglon.get("clave"))
            descripcion = safe_string(renglon.get("descripcion"), save_enie=True)
            descripcion_corta = safe_string(renglon.get("descripcion_corta"), save_enie=True)
            es_activo = renglon.get("es_activo") == "1"
            es_jurisdiccional = renglon.get("es_jurisdiccional") == "1"
            estatus = renglon.get("estatus")
            distrito = Distrito.query.filter(Distrito.clave == distrito_clave).first()
            if distrito is None:
                console.print(f"[yellow]El distrito {distrito_clave} no existe. Se omite la autoridad {clave}.[/yellow]")
                continue
            materia = Materia.query.filter(Materia.clave == materia_clave).first()
            if materia is None:
                console.print(f"[yellow]La materia {materia_clave} no existe. Se omite la autoridad {clave}.[/yellow]")
                continue
            autoridad = Autoridad(
                distrito=distrito,
                materia=materia,
                clave=clave,
                descripcion=descripcion,
                descripcion_corta=descripcion_corta,
                es_activo=es_activo,
                es_jurisdiccional=es_jurisdiccional,
                estatus=estatus,
            )
            autoridad.save()
            contador += 1

    # Mensaje de éxito
    console.print(f"  [green]{contador} autoridades alimentadas.[/green]")
