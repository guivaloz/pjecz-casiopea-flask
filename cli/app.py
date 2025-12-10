"""
PJECZ Fornax CLI
"""

from typer import Typer

from cli.commands.autoridades import autoridades
from cli.commands.bitacoras import bitacoras
from cli.commands.db import db
from cli.commands.distritos import distritos
from cli.commands.domicilios import domicilios
from cli.commands.materias import materias
from cli.commands.modulos import modulos
from cli.commands.permisos import permisos
from cli.commands.roles import roles
from cli.commands.usuarios import usuarios
from cli.commands.usuarios_roles import usuarios_roles

cli = Typer()
cli.add_typer(autoridades, name="autoridades")
cli.add_typer(bitacoras, name="bitacoras")
cli.add_typer(db, name="db")
cli.add_typer(distritos, name="distritos")
cli.add_typer(domicilios, name="domicilios")
cli.add_typer(materias, name="materias")
cli.add_typer(modulos, name="modulos")
cli.add_typer(permisos, name="permisos")
cli.add_typer(roles, name="roles")
cli.add_typer(usuarios, name="usuarios")
cli.add_typer(usuarios_roles, name="usuarios_roles")


if __name__ == "__main__":
    cli()
