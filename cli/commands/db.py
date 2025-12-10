"""
CLI Commands Database
"""

from rich.console import Console
from typer import Typer

from cli.commands.autoridades import alimentar as alimentar_autoridades
from cli.commands.distritos import alimentar as alimentar_distritos
from cli.commands.domicilios import alimentar as alimentar_domicilios
from cli.commands.materias import alimentar as alimentar_materias
from cli.commands.modulos import alimentar as alimentar_modulos
from cli.commands.permisos import alimentar as alimentar_permisos
from cli.commands.roles import alimentar as alimentar_roles
from cli.commands.usuarios import alimentar as alimentar_usuarios
from cli.commands.usuarios_roles import alimentar as alimentar_usuarios_roles
from pjecz_casiopea_flask.main import app, database

app.app_context().push()

db = Typer()


@db.command()
def inicializar():
    """Inicializar la base de datos"""
    console = Console()
    console.print("Inicializando la base de datos...")
    database.drop_all()
    database.create_all()


@db.command()
def alimentar():
    """Alimentar la base de datos con datos iniciales"""
    alimentar_materias()
    alimentar_distritos()
    alimentar_autoridades()
    alimentar_modulos()
    alimentar_roles()
    alimentar_permisos()
    alimentar_usuarios()
    alimentar_usuarios_roles()
    alimentar_domicilios()


@db.command()
def reiniciar():
    """Reiniciar la base de datos"""
    inicializar()
    alimentar()
