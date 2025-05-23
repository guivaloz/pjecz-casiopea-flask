"""
Materias, vistas
"""

import json

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..bitacoras.models import Bitacora
from ..materias.forms import MateriaForm
from ..materias.models import Materia
from ..modulos.models import Modulo
from ..permisos.models import Permiso
from ..usuarios.decorators import permission_required
from ...lib.datatables import get_datatable_parameters, output_datatable_json
from ...lib.safe_string import safe_clave, safe_message, safe_string

MODULO = "MATERIAS"

materias = Blueprint("materias", __name__, template_folder="templates")


@materias.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@materias.route("/materias/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Materias"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = Materia.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    # Ordenar y paginar
    registros = consulta.order_by(Materia.nombre).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "clave": resultado.clave,
                    "url": url_for("materias.detail", materia_id=resultado.id),
                },
                "nombre": resultado.nombre,
                "en_sentencias": resultado.en_sentencias,
                "en_exh_exhortos": resultado.en_exh_exhortos,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@materias.route("/materias/select_json", methods=["GET", "POST"])
def select_json():
    """Select JSON para materias"""
    # Consultar
    consulta = Materia.query.filter_by(estatus="A").order_by(Materia.nombre)
    # Elaborar datos para Select
    data = []
    for resultado in consulta.all():
        data.append(
            {
                "id": resultado.id,
                "nombre": resultado.nombre,
            }
        )
    # Entregar JSON
    return json.dumps(data)


@materias.route("/materias")
def list_active():
    """Listado de Materias activas"""
    return render_template(
        "materias/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Materias",
        estatus="A",
    )


@materias.route("/materias/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Materias inactivas"""
    return render_template(
        "materias/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Materias inactivos",
        estatus="B",
    )


@materias.route("/materias/<materia_id>")
def detail(materia_id):
    """Detalle de una Materia"""
    materia = Materia.query.get_or_404(materia_id)
    return render_template("materias/detail.jinja2", materia=materia)


@materias.route("/materias/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nueva Materia"""
    form = MateriaForm()
    if form.validate_on_submit():
        es_valido = True
        # Validar que la clave no se repita
        clave = safe_clave(form.clave.data)
        if Materia.query.filter_by(clave=clave).first():
            flash("La clave ya está en uso. Debe de ser única.", "warning")
            es_valido = False
        # Validar que el nombre no se repita
        nombre = safe_string(form.nombre.data, save_enie=True)
        if Materia.query.filter_by(nombre=nombre).first():
            flash("La nombre ya está en uso. Debe de ser único.", "warning")
            es_valido = False
        if es_valido:
            materia = Materia(
                clave=clave,
                nombre=nombre,
                descripcion=safe_string(form.descripcion.data, save_enie=True, to_uppercase=False),
                en_sentencias=form.en_sentencias.data,
                en_exh_exhortos=form.en_exh_exhortos.data,
            )
            materia.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nueva materia {materia.nombre}"),
                url=url_for("materias.detail", materia_id=materia.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    return render_template("materias/new.jinja2", form=form)


@materias.route("/materias/edicion/<materia_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(materia_id):
    """Editar Materia"""
    materia = Materia.query.get_or_404(materia_id)
    form = MateriaForm()
    if form.validate_on_submit():
        es_valido = True
        # Si cambia la clave verificar que no este en uso
        clave = safe_clave(form.clave.data)
        if materia.clave != clave:
            materia_existente = Materia.query.filter_by(clave=clave).first()
            if materia_existente and materia_existente.id != materia.id:
                es_valido = False
                flash("La clave ya está en uso. Debe de ser única.", "warning")
        # Si cambia el nombre verificar que no este en uso
        nombre = safe_string(form.nombre.data, save_enie=True)
        if materia.nombre != nombre:
            materia_existente = Materia.query.filter_by(nombre=nombre).first()
            if materia_existente and materia_existente.id != materia.id:
                es_valido = False
                flash("El nombre ya está en uso. Debe de ser único.", "warning")
        # Si es valido actualizar
        if es_valido:
            materia.clave = clave
            materia.nombre = nombre
            materia.descripcion = safe_string(form.descripcion.data, save_enie=True, to_uppercase=False)
            materia.en_sentencias = form.en_sentencias.data
            materia.en_exh_exhortos = form.en_exh_exhortos.data
            materia.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editada materia {materia.nombre}"),
                url=url_for("materias.detail", materia_id=materia.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.clave.data = materia.clave
    form.nombre.data = materia.nombre
    form.descripcion.data = materia.descripcion
    form.en_sentencias.data = materia.en_sentencias
    form.en_exh_exhortos.data = materia.en_exh_exhortos
    return render_template("materias/edit.jinja2", form=form, materia=materia)


@materias.route("/materias/eliminar/<materia_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(materia_id):
    """Eliminar Materia"""
    materia = Materia.query.get_or_404(materia_id)
    if materia.estatus == "A":
        materia.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminada materia {materia.nombre}"),
            url=url_for("materias.detail", materia_id=materia.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("materias.detail", materia_id=materia.id))


@materias.route("/materias/recuperar/<materia_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(materia_id):
    """Recuperar Materia"""
    materia = Materia.query.get_or_404(materia_id)
    if materia.estatus == "B":
        materia.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperada materia {materia.nombre}"),
            url=url_for("materias.detail", materia_id=materia.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("materias.detail", materia_id=materia.id))
