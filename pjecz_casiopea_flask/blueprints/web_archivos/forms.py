"""
Web Archivos, formularios
"""

from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class WebArchivoNewForm(FlaskForm):
    """Formulario WebArchivo"""

    clave = StringField("Clave (letras mayúsculas y números, hasta 14 caracteres)", validators=[DataRequired(), Length(max=14)])
    descripcion = StringField("Descripción (letras mayúsculas y números)", validators=[DataRequired(), Length(max=256)])
    titulo = StringField("Título", validators=[DataRequired(), Length(max=256)])
    archivo = StringField("Archivo", validators=[DataRequired(), Length(max=256)])
    url = StringField("URL", validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField("Guardar")


class WebArchivoEditForm(FlaskForm):
    """Formulario WebArchivo"""

    clave = StringField("Clave (letras mayúsculas y números, hasta 14 caracteres)", validators=[DataRequired(), Length(max=14)])
    descripcion = StringField("Descripción (letras mayúsculas y números)", validators=[DataRequired(), Length(max=256)])
    titulo = StringField("Título", validators=[DataRequired(), Length(max=256)])
    archivo = StringField("Archivo", validators=[DataRequired(), Length(max=256)])
    url = StringField("URL", validators=[DataRequired(), Length(max=256)])
    esta_archivado = BooleanField("Está archivado", validators=[Optional()])
    guardar = SubmitField("Guardar")
