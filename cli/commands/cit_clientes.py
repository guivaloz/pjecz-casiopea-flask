"""
CLI Commands Cit Clientes
"""

import random
from datetime import datetime, timedelta

from faker import Faker
from rich.console import Console
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from typer import Typer

from pjecz_casiopea_flask.blueprints.cit_clientes.models import CitCliente
from pjecz_casiopea_flask.config.extensions import pwd_context
from pjecz_casiopea_flask.lib.curp_generator import generar_curp_falso, generar_nacimiento_falso
from pjecz_casiopea_flask.lib.pwgen import generar_contrasena
from pjecz_casiopea_flask.lib.safe_string import safe_email, safe_string
from pjecz_casiopea_flask.main import app

LIMITE_CITAS_PENDIENTES = 3
RENOVACION_DIAS = 365

app.app_context().push()

cit_clientes = Typer()


@cit_clientes.command()
def agregar_falsos(cantidad: int = 10):
    """Agregar clientes con datos falsos para pruebas"""
    console = Console()
    faker = Faker(locale="es_MX")
    for _ in range(1, cantidad + 1):
        nombres = safe_string(faker.first_name(), save_enie=True)
        apellido_primero = safe_string(faker.last_name(), save_enie=True)
        apellido_segundo = safe_string(faker.last_name(), save_enie=True)
        contrasena = generar_contrasena()
        cit_cliente = CitCliente(
            nombres=nombres,
            apellido_primero=apellido_primero,
            apellido_segundo=apellido_segundo,
            curp=generar_curp_falso(nombres, apellido_primero, apellido_segundo, generar_nacimiento_falso()),
            telefono="".join(random.choices("0123456789", k=10)),
            email=faker.safe_email(),
            contrasena_md5="",
            contrasena_sha256=pwd_context.hash(contrasena),
            renovacion=datetime.now() + timedelta(days=RENOVACION_DIAS),
            limite_citas_pendientes=LIMITE_CITAS_PENDIENTES,
        )
        cit_cliente.save()
        console.print(f"+ {cit_cliente.email}: {contrasena}")
    console.print(f"[green]Se han agregado {cantidad} clientes falsos[/green]")


@cit_clientes.command()
def cambiar_contrasena(email: str):
    """Cambiar la contraseña de un cliente"""
    console = Console()
    try:
        email = safe_email(email)
    except ValueError:
        console.print("[yellow]No es válido el email[/yellow]")
        return
    try:
        cit_cliente = CitCliente.query.filter_by(email=email).one()
    except (MultipleResultsFound, NoResultFound):
        console.print("[yellow]No se encontró el cliente[/yellow]")
        return
    contrasena = generar_contrasena()
    cit_cliente.contrasena_md5 = ""
    cit_cliente.contrasena_sha256 = pwd_context.hash(contrasena)
    cit_cliente.renovacion = datetime.now() + timedelta(days=RENOVACION_DIAS)
    cit_cliente.save()
    console.print(f"[green]Se ha cambiado la contraseña de {email} a {contrasena}[/green]")
