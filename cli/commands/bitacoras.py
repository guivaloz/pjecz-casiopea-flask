"""
CLI Commands Bitácoras
"""

import os

from dotenv import load_dotenv
from rich.console import Console
from typer import Typer

from pjecz_casiopea_flask.main import task_queue

# Cargar las variables de entorno
load_dotenv()
SENDGRID_TO_EMAIL = os.getenv("SENDGRID_TO_EMAIL", "")

bitacoras = Typer()


@bitacoras.command()
def enviar_email_reporte():
    """Enviar reporte de bitácoras por email"""
    console = Console()
    console.print("[cyan]Enviando reporte de bitácoras por email...[/cyan]")
    tarea = task_queue.enqueue("pjecz_lira_flask.blueprints.bitacoras.tasks.enviar_reporte_por_email", SENDGRID_TO_EMAIL)
    console.print(f"[green]Se ha solicitado la tarea {tarea.id}[/green]")
