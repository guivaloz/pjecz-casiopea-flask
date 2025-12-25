"""
Domicilios, vistas
"""

import json

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ...lib.datatables import get_datatable_parameters, output_datatable_json
from ...lib.safe_string import safe_clave, safe_message, safe_string, safe_uuid
from ..bitacoras.models import Bitacora
from ..modulos.models import Modulo
from ..permisos.models import Permiso
from ..usuarios.decorators import permission_required
from .forms import DomicilioForm
from .models import Domicilio

MODULO = "DOMICILIOS"

domicilios = Blueprint("domicilios", __name__, template_folder="templates")


@domicilios.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@domicilios.route("/domicilios/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Domicilios"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = Domicilio.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter(Domicilio.estatus == request.form["estatus"])
    else:
        consulta = consulta.filter(Domicilio.estatus == "A")
    if "clave" in request.form:
        try:
            clave = safe_clave(request.form["clave"])
            if clave != "":
                consulta = consulta.filter(Domicilio.clave.contains(clave))
        except ValueError:
            pass
    if "edificio" in request.form:
        edificio = safe_string(request.form["edificio"], save_enie=True)
        if edificio != "":
            consulta = consulta.filter(Domicilio.edificio.contains(edificio))
    # Ordenar y paginar
    registros = consulta.order_by(Domicilio.edificio).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "clave": resultado.clave,
                    "url": url_for("domicilios.detail", domicilio_id=resultado.id),
                },
                "edificio": resultado.edificio,
                "estado": resultado.estado,
                "municipio": resultado.municipio,
                "calle": resultado.calle,
                "num_ext": resultado.num_ext,
                "num_int": resultado.num_int,
                "colonia": resultado.colonia,
                "cp": resultado.cp,
                "toggle_es_activo": {
                    "id": resultado.id,
                    "es_activo": resultado.es_activo,
                    "url": (
                        url_for("domicilios.toggle_es_activo_json", domicilio_id=resultado.id)
                        if current_user.can_edit(MODULO)
                        else ""
                    ),
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@domicilios.route("/domicilios")
def list_active():
    """Listado de Domicilios activos"""
    return render_template(
        "domicilios/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Domicilios",
        estatus="A",
    )


@domicilios.route("/domicilios/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Domicilios inactivos"""
    return render_template(
        "domicilios/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Domicilios inactivos",
        estatus="B",
    )


@domicilios.route("/domicilios/<domicilio_id>")
def detail(domicilio_id):
    """Detalle de un Domicilio"""
    domicilio_id = safe_uuid(domicilio_id)
    if domicilio_id == "":
        abort(400)
    domicilio = Domicilio.query.get_or_404(domicilio_id)
    return render_template("domicilios/detail.jinja2", domicilio=domicilio)


@domicilios.route("/domicilios/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Domicilio"""
    form = DomicilioForm()
    if form.validate_on_submit():
        clave = safe_clave(form.clave.data, max_len=32)
        edificio = safe_string(form.edificio.data, max_len=64, save_enie=True)
        estado = safe_string(form.estado.data, max_len=64, save_enie=True)
        municipio = safe_string(form.municipio.data, max_len=64, save_enie=True)
        calle = safe_string(form.calle.data, max_len=256, save_enie=True)
        num_ext = safe_string(form.num_ext.data, max_len=24, save_enie=True)
        num_int = safe_string(form.num_int.data, max_len=24, save_enie=True)
        colonia = safe_string(form.colonia.data, max_len=256, save_enie=True)
        cp = form.cp.data
        es_activo = form.es_activo.data
        # Validar que la clave no se repita
        if Domicilio.query.filter_by(clave=clave).first():
            flash("La clave ya está en uso. Debe de ser única.", "warning")
            return render_template("domicilios/new.jinja2", form=form)
        # Validar que el edificio no se repita
        if Domicilio.query.filter_by(edificio=edificio).first():
            flash("Ese edificio ya está en uso. Debe de ser único.", "warning")
            return render_template("domicilios/new.jinja2", form=form)
        # Guardar
        domicilio = Domicilio(
            clave=clave,
            edificio=edificio,
            estado=estado,
            municipio=municipio,
            calle=calle,
            num_ext=num_ext,
            num_int=num_int,
            colonia=colonia,
            cp=cp,
            completo=f"{calle} #{num_ext} {num_int}, {colonia}, {municipio}, {estado}, C.P. {cp}",
            es_activo=es_activo,
        )
        domicilio.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo Domicilio {domicilio.edificio}"),
            url=url_for("domicilios.detail", domicilio_id=domicilio.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("domicilios/new.jinja2", form=form)


@domicilios.route("/domicilios/edicion/<domicilio_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(domicilio_id):
    """Editar Domicilio"""
    domicilio_id = safe_uuid(domicilio_id)
    if domicilio_id == "":
        abort(400)
    domicilio = Domicilio.query.get_or_404(domicilio_id)
    form = DomicilioForm()
    if form.validate_on_submit():
        es_valido = True
        # Si cambia la clave verificar que no este en uso
        clave = safe_clave(form.clave.data, max_len=32)
        if domicilio.clave != clave:
            domicilio_existente = Domicilio.query.filter_by(clave=clave).first()
            if domicilio_existente and domicilio_existente.id != domicilio_id:
                es_valido = False
                flash("La clave ya está en uso. Debe de ser única.", "warning")
        # Si cambia el edificio verificar que no este en uso
        edificio = safe_string(form.edificio.data, max_len=64, save_enie=True)
        if domicilio.edificio != edificio:
            domicilio_existente = Domicilio.query.filter_by(edificio=edificio).first()
            if domicilio_existente and domicilio_existente.id != domicilio_id:
                es_valido = False
                flash("El edificio ya está en uso. Debe de ser único.", "warning")
        # Si es valido actualizar
        if es_valido:
            domicilio.clave = clave
            domicilio.edificio = safe_string(form.edificio.data, max_len=64, save_enie=True)
            domicilio.estado = safe_string(form.estado.data, max_len=64, save_enie=True)
            domicilio.municipio = safe_string(form.municipio.data, max_len=64, save_enie=True)
            domicilio.calle = safe_string(form.calle.data, max_len=256, save_enie=True)
            domicilio.num_ext = safe_string(form.num_ext.data, max_len=24, save_enie=True)
            domicilio.num_int = safe_string(form.num_int.data, max_len=24, save_enie=True)
            domicilio.colonia = safe_string(form.colonia.data, max_len=256, save_enie=True)
            domicilio.cp = form.cp.data
            domicilio.completo = domicilio.elaborar_completo()
            domicilio.es_activo = form.es_activo.data
            domicilio.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editado Domicilio {domicilio.edificio}"),
                url=url_for("domicilios.detail", domicilio_id=domicilio.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.clave.data = domicilio.clave
    form.edificio.data = domicilio.edificio
    form.estado.data = domicilio.estado
    form.municipio.data = domicilio.municipio
    form.calle.data = domicilio.calle
    form.num_ext.data = domicilio.num_ext
    form.num_int.data = domicilio.num_int
    form.colonia.data = domicilio.colonia
    form.cp.data = domicilio.cp
    form.es_activo.data = domicilio.es_activo
    return render_template("domicilios/edit.jinja2", form=form, domicilio=domicilio)


@domicilios.route("/domicilios/eliminar/<domicilio_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(domicilio_id):
    """Eliminar Domicilio"""
    domicilio_id = safe_uuid(domicilio_id)
    if domicilio_id == "":
        abort(400)
    domicilio = Domicilio.query.get_or_404(domicilio_id)
    if domicilio.estatus == "A":
        domicilio.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado Domicilio {domicilio.edificio}"),
            url=url_for("domicilios.detail", domicilio_id=domicilio.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("domicilios.detail", domicilio_id=domicilio.id))


@domicilios.route("/domicilios/recuperar/<domicilio_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(domicilio_id):
    """Recuperar Domicilio"""
    domicilio_id = safe_uuid(domicilio_id)
    if domicilio_id == "":
        abort(400)
    domicilio = Domicilio.query.get_or_404(domicilio_id)
    if domicilio.estatus == "B":
        domicilio.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado Domicilio {domicilio.edificio}"),
            url=url_for("domicilios.detail", domicilio_id=domicilio.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("domicilios.detail", domicilio_id=domicilio.id))


@domicilios.route("/domicilios/select_json", methods=["GET", "POST"])
def select_json():
    """Proporcionar el JSON de domicilios para elegir con un select"""
    consulta = Domicilio.query.filter_by(estatus="A").order_by(Domicilio.clave)
    data = []
    for resultado in consulta.all():
        data.append({"id": str(resultado.id), "texto": f"{resultado.clave}: {resultado.edificio}"})
    return json.dumps(data)


@domicilios.route("/domicilios/toggle_es_activo_json/<domicilio_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.ADMINISTRAR)
def toggle_es_activo_json(domicilio_id):
    """Cambiar es_activo a su opuesto al dar clic a su boton en datatable"""

    # Consultar
    domicilio_id = safe_uuid(domicilio_id)
    if domicilio_id == "":
        return {"success": False, "message": "No es un UUID válido"}
    domicilio = Domicilio.query.get_or_404(domicilio_id)
    if domicilio is None:
        return {"success": False, "message": "No encontrado"}

    # Cambiar es_activo a su opuesto y guardar
    domicilio.es_activo = not domicilio.es_activo
    domicilio.save()

    # Entregar JSON
    return {
        "success": True,
        "message": "Activo" if domicilio.es_activo == "A" else "Inactivo",
        "es_activo": domicilio.es_activo,
        "id": domicilio.id,
    }
