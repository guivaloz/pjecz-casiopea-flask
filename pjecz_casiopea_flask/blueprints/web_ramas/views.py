"""
Web Ramas, vistas
"""

import json

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ...lib.datatables import get_datatable_parameters, output_datatable_json
from ...lib.safe_string import safe_clave, safe_message, safe_path, safe_string
from ..bitacoras.models import Bitacora
from ..modulos.models import Modulo
from ..permisos.models import Permiso
from ..usuarios.decorators import permission_required
from .forms import WebRamaEditForm, WebRamaNewForm
from .models import WebRama

MODULO = "WEB RAMAS"

web_ramas = Blueprint("web_ramas", __name__, template_folder="templates")


@web_ramas.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@web_ramas.route("/web_ramas/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Web Ramas"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = WebRama.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter(WebRama.estatus == request.form["estatus"])
    else:
        consulta = consulta.filter(WebRama.estatus == "A")
    if "clave" in request.form:
        clave = safe_clave(request.form["clave"])
        if clave != "":
            consulta = consulta.filter(WebRama.clave.contains(clave))
    if "descripcion" in request.form:
        descripcion = safe_string(request.form["descripcion"], save_enie=True)
        if descripcion != "":
            consulta = consulta.filter(WebRama.descripcion.contains(descripcion))
    if "esta_archivado" in request.form:
        consulta = consulta.filter(WebRama.esta_archivado == bool(request.form["esta_archivado"]))
    # Ordenar y paginar
    registros = consulta.order_by(WebRama.clave).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "clave": resultado.clave,
                    "url": url_for("web_ramas.detail", web_rama_id=resultado.id),
                },
                "descripcion": resultado.descripcion,
                "titulo": resultado.titulo,
                "unidad_compartida": resultado.unidad_compartida,
                "directorio": resultado.directorio,
                "esta_archivado": resultado.esta_archivado,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@web_ramas.route("/web_ramas")
def list_active():
    """Listado de Web Ramas activas"""
    return render_template(
        "web_ramas/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Ramas",
        estatus="A",
    )


@web_ramas.route("/web_ramas/inactivos")
def list_inactive():
    """Listado de Web Ramas inactivas"""
    return render_template(
        "web_ramas/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Ramas inactivas",
        estatus="B",
    )


@web_ramas.route("/web_ramas/<web_rama_id>")
def detail(web_rama_id):
    """Detalle de un Web Rama"""
    web_rama = WebRama.query.get_or_404(web_rama_id)
    return render_template("web_ramas/detail.jinja2", web_rama=web_rama)


@web_ramas.route("/web_ramas/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nueva Web Rama"""
    form = WebRamaNewForm()
    if form.validate_on_submit():
        es_valido = True
        # Validar que la clave no se repita
        clave = safe_clave(form.clave.data)
        if WebRama.query.filter_by(clave=clave).first():
            flash("La clave ya está en uso. Debe de ser única.", "warning")
            es_valido = False
        # Si es válido, guardar
        if es_valido is True:
            web_rama = WebRama(
                clave=clave,
                descripcion=safe_string(form.descripcion.data, save_enie=True),
                titulo=safe_string(form.titulo.data, do_unidecode=False, save_enie=True, to_uppercase=False),
                unidad_compartida=form.unidad_compartida.data,
                directorio=form.directorio.data,
            )
            web_rama.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nueva Web Rama {web_rama.clave}"),
                url=url_for("web_ramas.detail", web_rama_id=web_rama.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    return render_template("web_ramas/new.jinja2", form=form)


@web_ramas.route("/web_ramas/edicion/<web_rama_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(web_rama_id):
    """Editar Web Rama"""
    web_rama = WebRama.query.get_or_404(web_rama_id)
    form = WebRamaEditForm()
    if form.validate_on_submit():
        es_valido = True
        # Si cambia la clave verificar que no está en uso
        clave = safe_clave(form.clave.data)
        if web_rama.clave != clave:
            web_rama_existente = WebRama.query.filter_by(clave=clave).first()
            if web_rama_existente and web_rama_existente.id != web_rama.id:
                es_valido = False
                flash("La clave ya está en uso. Debe de ser única.", "warning")
        # Si es válido, actualizar
        if es_valido:
            web_rama.clave = clave
            web_rama.descripcion = safe_string(form.descripcion.data, save_enie=True)
            web_rama.titulo = safe_string(form.titulo.data, do_unidecode=False, save_enie=True, to_uppercase=False)
            web_rama.unidad_compartida = form.unidad_compartida.data
            web_rama.directorio = form.directorio.data
            web_rama.esta_archivado = form.esta_archivado.data
            web_rama.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editado Web Rama {web_rama.clave}"),
                url=url_for("web_ramas.detail", web_rama_id=web_rama.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.clave.data = web_rama.clave
    form.descripcion.data = web_rama.descripcion
    form.titulo.data = web_rama.titulo
    form.unidad_compartida.data = web_rama.unidad_compartida
    form.directorio.data = web_rama.directorio
    form.esta_archivado.data = web_rama.esta_archivado
    return render_template("web_ramas/edit.jinja2", form=form, web_rama=web_rama)


@web_ramas.route("/web_ramas/eliminar/<web_rama_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(web_rama_id):
    """Eliminar Web Rama"""
    web_rama = WebRama.query.get_or_404(web_rama_id)
    if web_rama.estatus == "A":
        web_rama.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado Web Rama {web_rama.clave}"),
            url=url_for("web_ramas.detail", web_rama_id=web_rama.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("web_ramas.detail", web_rama_id=web_rama.id))


@web_ramas.route("/web_ramas/recuperar/<web_rama_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(web_rama_id):
    """Recuperar Web Rama"""
    web_rama = WebRama.query.get_or_404(web_rama_id)
    if web_rama.estatus == "B":
        web_rama.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado Web Rama {web_rama.clave}"),
            url=url_for("web_ramas.detail", web_rama_id=web_rama.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("web_ramas.detail", web_rama_id=web_rama.id))
