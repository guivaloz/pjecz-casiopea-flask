"""
Cit Clientes, vistas
"""

import json
from datetime import datetime, timedelta

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ...config.extensions import pwd_context
from ...lib.datatables import get_datatable_parameters, output_datatable_json
from ...lib.safe_string import safe_curp, safe_email, safe_message, safe_string, safe_uuid
from ..bitacoras.models import Bitacora
from ..modulos.models import Modulo
from ..permisos.models import Permiso
from ..usuarios.decorators import permission_required
from .forms import CitClienteForm
from .models import CitCliente

LIMITE_CITAS_PENDIENTES = 3
RENOVACION_DIAS = 365

MODULO = "CIT CLIENTES"

cit_clientes = Blueprint("cit_clientes", __name__, template_folder="templates")


@cit_clientes.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@cit_clientes.route("/cit_clientes/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Cit Cliente"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = CitCliente.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter(CitCliente.estatus == request.form["estatus"])
    else:
        consulta = consulta.filter(CitCliente.estatus == "A")
    if "email" in request.form:
        email = safe_email(request.form["email"], search_fragment=True)
        if email != "":
            consulta = consulta.filter(CitCliente.email.contains(email))
    if "nombres" in request.form:
        nombres = safe_string(request.form["nombres"], save_enie=True)
        if nombres != "":
            consulta = consulta.filter(CitCliente.nombres.contains(nombres))
    if "apellido_primero" in request.form:
        apellido_primero = safe_string(request.form["apellido_primero"], save_enie=True)
        if apellido_primero != "":
            consulta = consulta.filter(CitCliente.apellido_primero.contains(apellido_primero))
    if "apellido_segundo" in request.form:
        apellido_segundo = safe_string(request.form["apellido_segundo"], save_enie=True)
        if apellido_segundo != "":
            consulta = consulta.filter(CitCliente.apellido_segundo.contains(apellido_segundo))
    # Ordenar y paginar
    registros = consulta.order_by(CitCliente.email).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "email": resultado.email,
                    "url": url_for("cit_clientes.detail", cit_cliente_id=resultado.id),
                },
                "nombres": resultado.nombres,
                "apellido_primero": resultado.apellido_primero,
                "apellido_segundo": resultado.apellido_segundo,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@cit_clientes.route("/cit_clientes")
def list_active():
    """Listado de Cit Cliente activos"""
    return render_template(
        "cit_clientes/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Clientes",
        estatus="A",
    )


@cit_clientes.route("/cit_clientes/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Cit Cliente inactivos"""
    return render_template(
        "cit_clientes/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Clientes inactivos",
        estatus="B",
    )


@cit_clientes.route("/cit_clientes/<cit_cliente_id>")
def detail(cit_cliente_id):
    """Detalle de un Cit Cliente"""
    cit_cliente_id = safe_uuid(cit_cliente_id)
    if cit_cliente_id == "":
        abort(400)
    cit_cliente = CitCliente.query.get_or_404(cit_cliente_id)
    return render_template("cit_clientes/detail.jinja2", cit_cliente=cit_cliente)


@cit_clientes.route("/cit_clientes/new", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Cit Cliente"""
    form = CitClienteForm()
    if form.validate_on_submit():
        es_valido = True
        nombres = safe_string(form.nombres.data, save_enie=True)
        apellido_primero = safe_string(form.apellido_primero.data, save_enie=True)
        apellido_segundo = safe_string(form.apellido_segundo.data, save_enie=True)
        curp = form.curp.data  # Validado en el formulario
        telefono = form.telefono.data  # Validado en el formulario
        email = safe_email(form.email.data)
        contrasena = safe_string(form.contrasena.data, to_uppercase=False)
        limite_citas_pendientes = form.limite_citas_pendientes.data
        # Validar que el CURP no se repita
        if CitCliente.query.filter_by(curp=curp).first():
            flash("El CURP ya está en uso. Debe ser único.", "warning")
            es_valido = False
        # Validar que el email no se repita
        if CitCliente.query.filter_by(email=email).first():
            flash("El email ya está en uso. Debe ser único.", "warning")
            es_valido = False
        # Si es válido, guardar
        if es_valido:
            cit_cliente = CitCliente(
                nombres=nombres,
                apellido_primero=apellido_primero,
                apellido_segundo=apellido_segundo,
                curp=curp,
                telefono=telefono,
                email=email,
                contrasena_md5="",
                contrasena_sha256=pwd_context.hash(contrasena),
                renovacion=datetime.now() + timedelta(days=RENOVACION_DIAS),
                limite_citas_pendientes=limite_citas_pendientes,
            )
            cit_cliente.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nuevo Cliente {cit_cliente.email}"),
                url=url_for("cit_clientes.detail", cit_cliente_id=cit_cliente.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            # TODO: Agregar tarea en el fondo para enviar mensaje por correo electrónico
            return redirect(bitacora.url)
    form.limite_citas_pendientes.data = LIMITE_CITAS_PENDIENTES
    return render_template("cit_clientes/new.jinja2", form=form)


@cit_clientes.route("/cit_clientes/edicion/<cit_cliente_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(cit_cliente_id):
    """Editar Cit Cliente"""
    cit_cliente_id = safe_uuid(cit_cliente_id)
    if cit_cliente_id == "":
        abort(400)
    cit_cliente = CitCliente.query.get_or_404(cit_cliente_id)
    form = CitClienteForm()
    if form.validate_on_submit():
        es_valido = True
        nombres = safe_string(form.nombres.data, save_enie=True)
        apellido_primero = safe_string(form.apellido_primero.data, save_enie=True)
        apellido_segundo = safe_string(form.apellido_segundo.data, save_enie=True)
        curp = form.curp.data  # Validado en el formulario
        telefono = form.telefono.data  # Validado en el formulario
        email = safe_email(form.email.data)
        contrasena = safe_string(form.contrasena.data, to_uppercase=False)
        limite_citas_pendientes = form.limite_citas_pendientes.data
        # Si cambia el CURP verificar que no esté en uso
        if cit_cliente.curp != curp:
            cit_cliente_existente = CitCliente.query.filter_by(curp=curp).first()
            if cit_cliente_existente and cit_cliente_existente.id != cit_cliente.id:
                es_valido = False
                flash("El CURP ya está en uso. Debe ser único.", "warning")
        # Si cambia el email verificar que no esté en uso
        if cit_cliente.email != email:
            cit_cliente_existente = CitCliente.query.filter_by(email=email).first()
            if cit_cliente_existente and cit_cliente_existente.id != cit_cliente.id:
                es_valido = False
                flash("El email ya está en uso. Debe ser único.", "warning")
        # Si es válido, actualizar
        if es_valido:
            cit_cliente.nombres = nombres
            cit_cliente.apellido_primero = apellido_primero
            cit_cliente.apellido_segundo = apellido_segundo
            cit_cliente.curp = curp
            cit_cliente.telefono = telefono
            cit_cliente.email = email
            if contrasena != "":  # Solo si se escribe la contraseña, se cambia
                cit_cliente.contrasena_md5 = ""
                cit_cliente.contrasena_sha256 = pwd_context.hash(contrasena)
                cit_cliente.renovacion = datetime.now() + timedelta(days=RENOVACION_DIAS)
            cit_cliente.limite_citas_pendientes = limite_citas_pendientes
            cit_cliente.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editado Cliente {cit_cliente.email}"),
                url=url_for("cit_clientes.detail", cit_cliente_id=cit_cliente.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            # TODO: Agregar tarea en el fondo para enviar mensaje por correo electrónico
            return redirect(bitacora.url)
    form.nombres.data = cit_cliente.nombres
    form.apellido_primero.data = cit_cliente.apellido_primero
    form.apellido_segundo.data = cit_cliente.apellido_segundo
    form.curp.data = cit_cliente.curp
    form.telefono.data = cit_cliente.telefono
    form.email.data = cit_cliente.email
    form.contrasena.data = ""
    form.limite_citas_pendientes.data = cit_cliente.limite_citas_pendientes
    return render_template("cit_clientes/edit.jinja2", form=form, cit_cliente=cit_cliente)


@cit_clientes.route("/cit_clientes/eliminar/<cit_cliente_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(cit_cliente_id):
    """Eliminar Cit Cliente"""
    cit_cliente_id = safe_uuid(cit_cliente_id)
    if cit_cliente_id == "":
        abort(400)
    cit_cliente = CitCliente.query.get_or_404(cit_cliente_id)
    if cit_cliente.estatus == "A":
        cit_cliente.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado Cliente {cit_cliente.email}"),
            url=url_for("cit_clientes.detail", cit_cliente_id=cit_cliente.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("cit_clientes.detail", cit_cliente_id=cit_cliente.id))


@cit_clientes.route("/cit_clientes/recuperar/<cit_cliente_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(cit_cliente_id):
    """Recuperar Cit Cliente"""
    cit_cliente_id = safe_uuid(cit_cliente_id)
    if cit_cliente_id == "":
        abort(400)
    cit_cliente = CitCliente.query.get_or_404(cit_cliente_id)
    if cit_cliente.estatus == "B":
        cit_cliente.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado Cliente {cit_cliente.email}"),
            url=url_for("cit_clientes.detail", cit_cliente_id=cit_cliente.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("cit_clientes.detail", cit_cliente_id=cit_cliente.id))
