"""
CLI Commands Usuarios
"""

import csv
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from typer import Typer

from pjecz_casiopea_flask.blueprints.autoridades.models import Autoridad
from pjecz_casiopea_flask.blueprints.usuarios.models import Usuario
from pjecz_casiopea_flask.config.extensions import pwd_context
from pjecz_casiopea_flask.lib.pwgen import generar_contrasena
from pjecz_casiopea_flask.lib.safe_string import safe_clave, safe_email, safe_string
from pjecz_casiopea_flask.main import app, task_queue

# Cargar las variables de entorno
load_dotenv()
SENDGRID_TO_EMAIL = os.getenv("SENDGRID_TO_EMAIL", "")

USUARIOS_CSV = "seed/usuarios_roles.csv"

# Inicializar el contexto de la aplicación Flask
app.app_context().push()

usuarios = Typer()


@usuarios.command()
def alimentar():
    """Alimentar la base de datos con usuarios iniciales"""
    console = Console()
    console.print("Alimentando la base de datos con usuarios iniciales...")

    # Verificar que exista el archivo CSV
    ruta = Path(USUARIOS_CSV)
    if not ruta.is_file():
        console.print(f"[red]El archivo {USUARIOS_CSV} no existe.[/red]")
        return

    # Leer el archivo CSV e insertar
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        for renglon in csv.DictReader(puntero):
            autoridad_clave = safe_clave(renglon.get("autoridad_clave"))
            email = safe_email(renglon.get("email"))
            nombres = safe_string(renglon.get("nombres"), save_enie=True)
            apellido_paterno = safe_string(renglon.get("apellido_paterno"), save_enie=True)
            apellido_materno = safe_string(renglon.get("apellido_materno"), save_enie=True)
            puesto = safe_string(renglon.get("puesto"), save_enie=True)
            estatus = renglon.get("estatus")
            autoridad = Autoridad.query.filter(Autoridad.clave == autoridad_clave).first()
            if autoridad is None:
                console.print(f"[yellow]La autoridad {autoridad_clave} no existe. Se omite el usuario {email}.[/yellow]")
                continue
            usuario = Usuario(
                autoridad=autoridad,
                email=email,
                nombres=nombres,
                apellido_paterno=apellido_paterno,
                apellido_materno=apellido_materno,
                puesto=puesto,
                estatus=estatus,
                api_key="",
                api_key_expiracion=datetime(year=2000, month=1, day=1),
                contrasena=pwd_context.hash(generar_contrasena()),
            )
            usuario.save()
            contador += 1

    # Mensaje de éxito
    console.print(f"  [green]{contador} usuarios alimentados.[/green]")


@usuarios.command()
def enviar_email_reporte():
    """Enviar reporte de usuarios por email"""
    console = Console()
    console.print("[cyan]Enviando reporte de usuarios por email...[/cyan]")
    tarea = task_queue.enqueue("pjecz_lira_flask.blueprints.usuarios.tasks.enviar_reporte_por_email", SENDGRID_TO_EMAIL)
    console.print(f"[green]Se ha solicitado la tarea {tarea.id}[/green]")


@usuarios.command()
def nueva_contrasena(email: str):
    """Nueva contraseña para un usuario existente"""
    console = Console()
    usuario = Usuario.query.filter(Usuario.email == email).first()
    if usuario is None:
        console.print(f"[red]El usuario con email {email} no existe.[/red]")
        return
    contrasena = input("Contraseña: ")
    usuario.contrasena = pwd_context.hash(contrasena.strip())
    usuario.save()
    console.print(f"[green]Se ha actualizado la contraseña para el usuario {email}.[/green]")
