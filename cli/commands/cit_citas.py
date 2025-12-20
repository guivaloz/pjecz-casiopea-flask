"""
CLI Commands Cit Citas
"""

import random
from datetime import datetime, timedelta

from faker import Faker
from rich.console import Console
from sqlalchemy.sql import func
from typer import Typer

from pjecz_casiopea_flask.blueprints.cit_citas.models import CitCita
from pjecz_casiopea_flask.blueprints.cit_clientes.models import CitCliente
from pjecz_casiopea_flask.blueprints.cit_oficinas_servicios.models import CitOficinaServicio
from pjecz_casiopea_flask.blueprints.cit_servicios.models import CitServicio
from pjecz_casiopea_flask.blueprints.oficinas.models import Oficina
from pjecz_casiopea_flask.main import app

app.app_context().push()

cit_citas = Typer()


@cit_citas.command()
def agregar_falsos(maximo: int = 10, desde: str = "", hasta: str = ""):
    """Agregar citas con datos falsos"""
    console = Console()

    # Si no viene desde, usar el día de hoy
    if not desde:
        desde_dt = datetime.now().date()
    else:
        try:
            desde_dt = datetime.strptime(desde, "%Y-%m-%d").date()
        except ValueError:
            console.print("[yellow]Fecha 'desde' inválida[/yellow]")
            return

    # Si no viene hasta, usar 30 días después del día de hoy
    if not hasta:
        hasta_dt = datetime.now().date() + timedelta(days=30)
    else:
        try:
            hasta_dt = datetime.strptime(hasta, "%Y-%m-%d").date()
        except ValueError:
            console.print("[yellow]Fecha 'hasta' inválida[/yellow]")
            return

    # Consultar cit_clientes
    cit_clientes = CitCliente.query.filter(CitCliente.estatus == "A").order_by(CitCliente.creado.desc()).limit(10).all()

    # Si no hay cit_clientes, salir
    if not cit_clientes:
        console.print("[yellow]No hay clientes para asignar citas[/yellow]")
        return

    # Inicializar el contador
    contador = 0

    # Bucle entre los cit_clientes
    for cit_cliente in cit_clientes:
        # Bucle para agregar citas, de una a LIMITE_CITAS_CANTIDAD
        for _ in range(1, random.randint(1, maximo) + 1):
            # Definir una fecha aleatoria entre desde_dt y hasta_dt
            delta_dias = (hasta_dt - desde_dt).days
            fecha = desde_dt + timedelta(days=random.randint(0, delta_dias))
            # Definir una hora aleatoria entre 9:00 y 12:00
            hora = random.randint(9, 11)
            minuto = random.choice([0, 15, 30, 45])
            fecha_hora = datetime(fecha.year, fecha.month, fecha.day, hora, minuto)
            # Bucle hasta encontrar un servicio y oficina
            while True:
                # Consultar un CitServicio aleatorio
                cit_servicio = CitServicio.query.order_by(func.random()).first()
                if cit_servicio is None:
                    console.print("[yellow]No hay servicios para asignar citas[/yellow]")
                    return
                # Consultar una Oficina aleatoria
                oficina = Oficina.query.order_by(func.random()).first()
                if oficina is None:
                    console.print("[yellow]No hay oficinas para asignar citas[/yellow]")
                    return
                # Consultar si hay un CitOficinaServicio para el servicio y oficina
                cit_oficina_servicio = CitOficinaServicio.query.filter_by(
                    cit_servicio_id=cit_servicio.id,
                    oficina_id=oficina.id,
                ).first()
                # Si lo hay, salir el bucle
                if cit_oficina_servicio:
                    break
            # Crear la cita
            cit_cita = CitCita()
            cit_cita.cit_cliente_id = cit_cliente.id
            cit_cita.cit_servicio_id = cit_servicio.id
            cit_cita.oficina_id = oficina.id
            cit_cita.inicio = fecha_hora
            cit_cita.termino = fecha_hora + timedelta(hours=cit_servicio.duracion.hour, minutes=cit_servicio.duracion.minute)
            cit_cita.notas = Faker().sentence(nb_words=6)
            cit_cita.estado = "PENDIENTE"
            cit_cita.cancelar_antes = cit_cita.inicio - timedelta(hours=24)
            cit_cita.asistencia = False
            cit_cita.codigo_asistencia = "".join(random.choices("0123456789", k=6))
            cit_cita.save()
            contador += 1
    # Mensaje final
    console.print(f"[green]Se han agregado {contador} citas falsas[/green]")


@cit_citas.command()
def eliminar(horas: int = 24):
    """Eliminar citas pasadas"""
    console = Console()
    # Definir el tiempo límite
    tiempo_limite = datetime.now() - timedelta(hours=horas)
    # Consultar las citas a eliminar
    citas = CitCita.query.filter(CitCita.inicio < tiempo_limite).filter(CitCita.estatus == "A").all()
    # Contador
    contador = 0
    # Bucle entre las citas
    for cita in citas:
        cita.delete()
        contador += 1
    # Mensaje final
    console.print(f"[green]Se han eliminado {contador} citas pasadas de más de {horas} horas[/green]")
