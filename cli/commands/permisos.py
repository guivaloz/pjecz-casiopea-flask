"""
CLI Commands Permisos
"""

import csv
from pathlib import Path

from rich.console import Console
from typer import Typer

from pjecz_casiopea_flask.blueprints.modulos.models import Modulo
from pjecz_casiopea_flask.blueprints.permisos.models import Permiso
from pjecz_casiopea_flask.blueprints.roles.models import Rol
from pjecz_casiopea_flask.lib.safe_string import safe_string
from pjecz_casiopea_flask.main import app

PERMISOS_CSV = "seed/roles_permisos.csv"

app.app_context().push()

permisos = Typer()


@permisos.command()
def alimentar():
    """Alimentar la base de datos con permisos iniciales"""
    console = Console()
    console.print("Alimentando la base de datos con permisos iniciales...")

    # Verificar que exista el archivo CSV
    ruta = Path(PERMISOS_CSV)
    if not ruta.is_file():
        console.print(f"[red]El archivo {PERMISOS_CSV} no existe.[/red]")
        return

    # Consultar todos los módulos
    modulos = Modulo.query.order_by(Modulo.nombre).all()

    # Leer el archivo CSV e insertar
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        for renglon in csv.DictReader(puntero):
            rol_nombre = safe_string(renglon.get("rol_nombre"), save_enie=True)
            estatus = renglon["estatus"]
            rol = Rol.query.filter(Rol.nombre == rol_nombre).first()
            if rol is None:
                console.print(f"[yellow]El rol {rol_nombre} no existe. Se omiten sus permisos.[/yellow]")
                continue
            for modulo in modulos:
                columna = modulo.nombre.lower()
                if columna not in renglon:
                    continue
                if renglon[columna] == "":
                    continue
                try:
                    nivel = int(renglon[columna])
                except ValueError:
                    continue
                if nivel < 0:
                    nivel = 0
                if nivel > 4:
                    nivel = 4
                permiso = Permiso(
                    rol=rol,
                    modulo=modulo,
                    nivel=nivel,
                    nombre=f"{rol.nombre} puede {Permiso.NIVELES[nivel]} en {modulo.nombre}",
                    estatus=estatus,
                )
                permiso.save()
                contador += 1

    # Mensaje de éxito
    console.print(f"  [green]{contador} permisos alimentados.[/green]")
