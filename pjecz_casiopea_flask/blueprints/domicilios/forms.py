"""
Domicilios, formularios
"""

from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Regexp

from ...lib.safe_string import CLAVE_REGEXP


class DomicilioForm(FlaskForm):
    """Formulario Domicilio"""

    clave = StringField("Clave", validators=[DataRequired(), Regexp(CLAVE_REGEXP), Length(max=16)])
    edificio = StringField("Edificio", validators=[DataRequired(), Length(max=64)])
    estado = StringField("Estado", validators=[DataRequired(), Length(max=64)])
    municipio = StringField("Municipio", validators=[DataRequired(), Length(max=64)])
    calle = StringField("Calle", validators=[DataRequired(), Length(max=256)])
    num_ext = StringField("Núm. Exterior", validators=[Optional()])
    num_int = StringField("Núm. Interior", validators=[Optional()])
    colonia = StringField("Colonia", validators=[Optional(), Length(max=256)])
    cp = IntegerField("CP", validators=[DataRequired()])
    es_activo = BooleanField("Activo", validators=[Optional()], default=True)
    guardar = SubmitField("Guardar")
