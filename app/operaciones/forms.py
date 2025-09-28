
from ast import Str
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, SubmitField, TextAreaField, BooleanField, DateField,  SelectField, HiddenField)
from wtforms.fields import FloatField, IntegerField
from wtforms.validators import DataRequired, Length, Email, NumberRange


class AltaSolicitudesForm(FlaskForm):
    nombre_asegurado = StringField('Nombre del asegurado')
    vehiculo = StringField('Vehiculo')
    numero_riesgo = IntegerField('Número de riesgo en póliza')
    solicitud = IntegerField('Número de solicitud')
    patente = StringField('Patente')
    id_compania = SelectField('Compañías', choices =[( 0,'Seleccionar compañía')], coerce = int, default = None, validators=[DataRequired('Seleccione compania')])
