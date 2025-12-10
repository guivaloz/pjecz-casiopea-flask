"""
CLI Commands Usuarios-Roles
"""

import csv
from pathlib import Path

from rich.console import Console
from typer import Typer

from pjecz_casiopea_flask.blueprints.roles.models import Rol
from pjecz_casiopea_flask.blueprints.usuarios.models import Usuario
from pjecz_casiopea_flask.blueprints.usuarios_roles.models import UsuarioRol
from pjecz_casiopea_flask.lib.safe_string import safe_email, safe_string
from pjecz_casiopea_flask.main import app

USUARIOS_ROLES_CSV = "seed/usuarios_roles.csv"

app.app_context().push()

usuarios_roles = Typer()


@usuarios_roles.command()
def alimentar():
    """Alimentar la base de datos con usuarios_roles iniciales"""
    console = Console()
    console.print("Alimentando la base de datos con usuarios_roles iniciales...")

    # Verificar que exista el archivo CSV
    ruta = Path(USUARIOS_ROLES_CSV)
    if not ruta.is_file():
        console.print(f"[red]El archivo {USUARIOS_ROLES_CSV} no existe.[/red]")
        return

    # Leer el archivo CSV e insertar
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        for renglon in csv.DictReader(puntero):
            email = safe_email(renglon.get("email"))
            usuario = Usuario.query.filter(Usuario.email == email).first()
            if usuario is None:
                console.print(f"[yellow]El usuario {email} no existe. Se omiten sus roles.[/yellow]")
                continue
            roles_str = renglon.get("roles")
            if not roles_str:
                continue
            for rol_nombre in roles_str.split(","):
                nombre = safe_string(rol_nombre)
                rol = Rol.query.filter(Rol.nombre == nombre).first()
                if rol is None:
                    console.print(f"[yellow]El rol {nombre} no existe. Se omite para el usuario {email}.[/yellow]")
                    continue
                usuario_rol = UsuarioRol(
                    usuario=usuario,
                    rol=rol,
                    descripcion=f"{usuario.email} en {rol.nombre}",
                )
                usuario_rol.save()
                contador += 1

    # Mensaje de éxito
    console.print(f"  [green]{contador} usuarios_roles alimentados.[/green]")
