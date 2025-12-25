"""
Oficinas, formularios
"""

from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, SelectField, StringField, SubmitField, TimeField
from wtforms.validators import DataRequired, Length, Optional, Regexp

from ...lib.safe_string import CLAVE_REGEXP
from ..distritos.models import Distrito
from ..domicilios.models import Domicilio


class OficinaForm(FlaskForm):
    """Formulario Oficina"""

    clave = StringField("Clave", validators=[DataRequired(), Regexp(CLAVE_REGEXP), Length(max=16)])
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    descripcion_corta = StringField("Descripción Corta", validators=[DataRequired(), Length(max=64)])
    distrito = SelectField("Distrito", coerce=str, validators=[DataRequired()])
    domicilio = SelectField("Domicilio", coerce=str, validators=[DataRequired()])
    apertura = TimeField("Horario de apertura", validators=[DataRequired()], format="%H:%M")
    cierre = TimeField("Horario de cierre", validators=[DataRequired()], format="%H:%M")
    limite_personas = IntegerField("Límite de personas", validators=[DataRequired()])
    es_jurisdiccional = BooleanField("Es Jurisdiccional", validators=[Optional()])
    puede_agendar_citas = BooleanField("Puede agendar citas", validators=[Optional()])
    puede_enviar_qr = BooleanField("Puede enviar códigos QR", validators=[Optional()])
    es_activo = BooleanField("Activo", validators=[Optional()], default=True)
    guardar = SubmitField("Guardar")

    def __init__(self, *args, **kwargs):
        """Inicializar y cargar opciones en domicilio"""
        super().__init__(*args, **kwargs)
        self.distrito.choices = [
            (d.id, d.nombre_corto) for d in Distrito.query.filter_by(estatus="A").order_by(Distrito.nombre_corto).all()
        ]
        self.domicilio.choices = [
            (d.id, d.edificio) for d in Domicilio.query.filter_by(estatus="A").order_by(Domicilio.edificio).all()
        ]
