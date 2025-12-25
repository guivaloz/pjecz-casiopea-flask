"""
Cit Servicios, vistas
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
from .forms import CitServicioForm
from .models import CitServicio

DIAS_SEMANA = {
    0: "DOMINGO",
    1: "LUNES",
    2: "MARTES",
    3: "MIERCOLES",
    4: "JUEVES",
    5: "VIERNES",
    6: "SABADO",
}
MODULO = "CIT SERVICIOS"

cit_servicios = Blueprint("cit_servicios", __name__, template_folder="templates")


@cit_servicios.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@cit_servicios.route("/cit_servicios/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Cit Servicios"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = CitServicio.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter(CitServicio.estatus == request.form["estatus"])
    else:
        consulta = consulta.filter(CitServicio.estatus == "A")
    if "cit_categoria_id" in request.form:
        consulta = consulta.filter(CitServicio.cit_categoria_id == request.form["cit_categoria_id"])
    if "clave" in request.form:
        clave = safe_clave(request.form["clave"])
        if clave != "":
            consulta = consulta.filter(CitServicio.clave.contains(clave))
    if "descripcion" in request.form:
        descripcion = safe_string(request.form["descripcion"], save_enie=True)
        if descripcion != "":
            consulta = consulta.filter(CitServicio.descripcion.contains(descripcion))
    # Ordenar y paginar
    registros = consulta.order_by(CitServicio.clave).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "clave": resultado.clave,
                    "url": url_for("cit_servicios.detail", cit_servicio_id=resultado.id),
                },
                "descripcion": resultado.descripcion,
                "duracion": resultado.duracion.strftime("%H:%M"),
                "documentos_limite": resultado.documentos_limite,
                "cit_categoria": {
                    "nombre": resultado.cit_categoria.nombre,
                    "url": (
                        url_for("cit_categorias.detail", cit_categoria_id=resultado.cit_categoria.id)
                        if current_user.can_view("CIT CATEGORIAS")
                        else ""
                    ),
                },
                "desde": "-" if resultado.desde is None else resultado.desde.strftime("%H:%M"),
                "hasta": "-" if resultado.hasta is None else resultado.hasta.strftime("%H:%M"),
                "dias_habilitados": resultado.dias_habilitados,
                "toggle_es_activo": {
                    "id": resultado.id,
                    "es_activo": resultado.es_activo,
                    "url": (
                        url_for("cit_servicios.toggle_es_activo_json", cit_servicio_id=resultado.id)
                        if current_user.can_edit(MODULO)
                        else ""
                    ),
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@cit_servicios.route("/cit_servicios")
def list_active():
    """Listado de Cit Servicios activos"""
    return render_template(
        "cit_servicios/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Servicios",
        estatus="A",
    )


@cit_servicios.route("/cit_servicios/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Cit Servicios inactivos"""
    return render_template(
        "cit_servicios/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Servicios inactivos",
        estatus="B",
    )


@cit_servicios.route("/cit_servicios/<cit_servicio_id>")
def detail(cit_servicio_id):
    """Detalle de un Cit Servicio"""
    # Consultar
    cit_servicio_id = safe_uuid(cit_servicio_id)
    if cit_servicio_id == "":
        abort(400)
    cit_servicio = CitServicio.query.get_or_404(cit_servicio_id)
    # Convertir los dias habilitados a textos, por ejemplo "23" a "MARTES, MIERCOLES"
    dias_habilitados = ""
    for valor, dia in DIAS_SEMANA.items():
        if str(valor) in cit_servicio.dias_habilitados:
            dias_habilitados += f"{dia}, "
    if dias_habilitados == "":
        dias_habilitados = "De lunes a viernes"
    # Entregar
    return render_template(
        "cit_servicios/detail.jinja2",
        cit_servicio=cit_servicio,
        dias_habilitados=dias_habilitados,
    )


@cit_servicios.route("/cit_servicios/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Cit Servicio"""
    form = CitServicioForm()
    if form.validate_on_submit():
        es_valido = True
        # Validar clave
        clave = safe_clave(form.clave.data)
        if clave == "":
            es_valido = False
            flash("La clave es incorrecta o está vacía", "warning")
        # Validar que la clave sea única
        if CitServicio.query.filter_by(clave=clave).first():
            es_valido = False
            flash("La clave ya está en uso. Debe de ser único.", "warning")
        # Si documento limite es menor a 1, cambiar a 0
        if form.documentos_limite.data is None:
            documentos_limite = 0
        else:
            documentos_limite = form.documentos_limite.data
        if documentos_limite < 1:
            documentos_limite = 0
        # Tomar los tiempos desde y hasta
        desde = form.desde.data
        hasta = form.hasta.data
        # Si desde y hasta NO están vacíos, cambiar el desde y hasta si los valores estan invertidos
        if desde is not None and hasta is not None:
            if desde > hasta:
                desde, hasta = hasta, desde
        # Transformar el texto de los días habilitados, por ejemplo "MARTES, MIERCOLES" a "23"
        dias_habilitados = ""
        if form.dias_habilitados.data is None:
            dias_habilitados_input = ""
        else:
            dias_habilitados_input = form.dias_habilitados.data.strip()
        if dias_habilitados_input != "":
            for dia_seleccionado in dias_habilitados_input.split(","):
                dia_seleccionado = dia_seleccionado.strip().upper()
                for valor, dia in DIAS_SEMANA.items():
                    if dia == dia_seleccionado:
                        dias_habilitados += str(valor)
        # Si es válido, guardar
        if es_valido:
            cit_servicio = CitServicio(
                cit_categoria_id=form.cit_categoria.data,
                clave=clave,
                descripcion=safe_string(form.descripcion.data, save_enie=True, max_len=64),
                duracion=form.duracion.data,
                documentos_limite=documentos_limite,
                desde=desde,
                hasta=hasta,
                dias_habilitados=dias_habilitados,
                es_activo=form.es_activo.data,
            )
            cit_servicio.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nuevo Servicio {cit_servicio.clave}"),
                url=url_for("cit_servicios.detail", cit_servicio_id=cit_servicio.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    # Si viene cit_categoria_id en el URL, seleccionar esa categoría
    cit_categoria_id = request.args.get("cit_categoria_id")
    if cit_categoria_id is not None:
        try:
            cit_categoria_id = int(cit_categoria_id)
            form.cit_categoria.data = cit_categoria_id
        except ValueError:
            pass
    # Entregar formulario
    return render_template("cit_servicios/new.jinja2", form=form)


@cit_servicios.route("/cit_servicios/edicion/<cit_servicio_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(cit_servicio_id):
    """Editar Cit Servicio"""
    cit_servicio_id = safe_uuid(cit_servicio_id)
    if cit_servicio_id == "":
        abort(400)
    cit_servicio = CitServicio.query.get_or_404(cit_servicio_id)
    form = CitServicioForm()
    if form.validate_on_submit():
        es_valido = True
        # Validar clave
        clave = safe_clave(form.clave.data)
        if clave == "":
            es_valido = False
            flash("La clave es incorrecta o está vacía", "warning")
        # Si cambia la clave verificar que no este en uso
        if cit_servicio.clave != clave:
            cit_servicio_existente = CitServicio.query.filter_by(clave=clave).first()
            if cit_servicio_existente and cit_servicio_existente.id != cit_servicio.id:
                es_valido = False
                flash("La clave ya está en uso. Debe de ser única.", "warning")
        # Tomar los tiempos desde y hasta
        desde = form.desde.data
        hasta = form.hasta.data
        # Si desde y hasta NO están vacíos, cambiar el desde y hasta si los valores estan invertidos
        if desde is not None and hasta is not None:
            if desde > hasta:
                desde, hasta = hasta, desde
        # Transformar el texto de los días habilitados, por ejemplo "MARTES, MIERCOLES" a "23"
        dias_habilitados = ""
        if form.dias_habilitados.data is None:
            dias_habilitados_input = ""
        else:
            dias_habilitados_input = form.dias_habilitados.data.strip()
        if dias_habilitados_input != "":
            for dia_seleccionado in dias_habilitados_input.split(","):
                dia_seleccionado = dia_seleccionado.strip().upper()
                for valor, dia in DIAS_SEMANA.items():
                    if dia == dia_seleccionado:
                        dias_habilitados += str(valor)
        # Si es válido, actualizar
        if es_valido:
            cit_servicio.cit_categoria_id = form.cit_categoria.data  # Select que tiene el Id de cit_categoria
            cit_servicio.clave = clave
            cit_servicio.descripcion = safe_string(form.descripcion.data, save_enie=True, max_len=64)
            cit_servicio.duracion = form.duracion.data
            cit_servicio.documentos_limite = form.documentos_limite.data
            cit_servicio.desde = desde
            cit_servicio.hasta = hasta
            cit_servicio.dias_habilitados = dias_habilitados
            cit_servicio.es_activo = form.es_activo.data
            cit_servicio.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editado Servicio {cit_servicio.clave}"),
                url=url_for("cit_servicios.detail", cit_servicio_id=cit_servicio.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    # Convertir los dias habilitados a textos, por ejemplo "23" a "MARTES, MIERCOLES"
    dias_habilitados = ""
    for valor, dia in DIAS_SEMANA.items():
        if str(valor) in cit_servicio.dias_habilitados:
            dias_habilitados += f"{dia}, "
    # Definir valores en el formulario
    form.cit_categoria.data = cit_servicio.cit_categoria_id  # Select que necesita el ID de cit_categoria
    form.clave.data = cit_servicio.clave
    form.descripcion.data = cit_servicio.descripcion
    form.duracion.data = cit_servicio.duracion
    form.documentos_limite.data = cit_servicio.documentos_limite
    form.desde.data = cit_servicio.desde
    form.hasta.data = cit_servicio.hasta
    form.dias_habilitados.data = dias_habilitados
    form.es_activo.data = cit_servicio.es_activo
    # Entregar formulario
    return render_template("cit_servicios/edit.jinja2", form=form, cit_servicio=cit_servicio)


@cit_servicios.route("/cit_servicios/eliminar/<cit_servicio_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(cit_servicio_id):
    """Eliminar Cit Servicio"""
    cit_servicio_id = safe_uuid(cit_servicio_id)
    if cit_servicio_id == "":
        abort(400)
    cit_servicio = CitServicio.query.get_or_404(cit_servicio_id)
    if cit_servicio.estatus == "A":
        cit_servicio.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado Servicio {cit_servicio.clave}"),
            url=url_for("cit_servicios.detail", cit_servicio_id=cit_servicio.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("cit_servicios.detail", cit_servicio_id=cit_servicio.id))


@cit_servicios.route("/cit_servicios/recuperar/<cit_servicio_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(cit_servicio_id):
    """Recuperar Cit Servicio"""
    cit_servicio_id = safe_uuid(cit_servicio_id)
    if cit_servicio_id == "":
        abort(400)
    cit_servicio = CitServicio.query.get_or_404(cit_servicio_id)
    if cit_servicio.estatus == "B":
        cit_servicio.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado Servicio {cit_servicio.clave}"),
            url=url_for("cit_servicios.detail", cit_servicio_id=cit_servicio.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("cit_servicios.detail", cit_servicio_id=cit_servicio.id))


@cit_servicios.route("/cit_servicios/toggle_es_activo_json/<cit_servicio_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.ADMINISTRAR)
def toggle_es_activo_json(cit_servicio_id):
    """Cambiar es_activo a su opuesto al dar clic a su boton en datatable"""

    # Consultar
    cit_servicio_id = safe_uuid(cit_servicio_id)
    if cit_servicio_id == "":
        return {"success": False, "message": "No es un UUID válido"}
    cit_servicio = CitServicio.query.get_or_404(cit_servicio_id)
    if cit_servicio is None:
        return {"success": False, "message": "No encontrado"}

    # Cambiar es_activo a su opuesto y guardar
    cit_servicio.es_activo = not cit_servicio.es_activo
    cit_servicio.save()

    # Entregar JSON
    return {
        "success": True,
        "message": "Activo" if cit_servicio.es_activo == "A" else "Inactivo",
        "es_activo": cit_servicio.es_activo,
        "id": cit_servicio.id,
    }
