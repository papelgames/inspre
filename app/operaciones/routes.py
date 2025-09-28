import logging

from datetime import date, datetime, timedelta

from flask import render_template, redirect, url_for, abort, current_app, flash, request
from flask_login import login_required, current_user

from app.auth.decorators import admin_required, not_initial_status
from app.auth.models import Users
from app.models import  Estados, Companias, Solicitudes

from . import operaciones_bp 
from .forms import AltaSolicitudesForm


logger = logging.getLogger(__name__)

def control_vencimiento (fecha):
    if fecha < datetime.now():
        return "VENCIDO"

#creo una tupla para usar en el campo select del form que quiera que necesite las companias
def companias_select():
    companias = Companias.get_all()
    select_companias =[(0,'Seleccionar Compania')]
    for rs in companias:
        sub_select_companias = (rs.id, rs.nombre_compania)
        select_companias.append(sub_select_companias)
    return select_companias

@operaciones_bp.route("/operaciones/altasolicitudes/", methods = ['GET', 'POST'])
@login_required
@not_initial_status
def alta_solicitudes():

    form = AltaSolicitudesForm()
    form.id_compania.choices = companias_select()

    if form.validate_on_submit():
        nombre_asegurado = form.nombre_asegurado.data
        vehiculo = form.vehiculo.data
        numero_riesgo = form.numero_riesgo.data
        solicitud = form.solicitud.data
        patente = form.patente.data
        id_compania = form.id_compania.data
        estado = Estados.get_first_by_clave_tabla(1, 'solicitudes')
        nueva_solicitud = Solicitudes(nombre_asegurado = nombre_asegurado,
                                    vehiculo = vehiculo,
                                    numero_riesgo = numero_riesgo,
                                    solicitud = solicitud,
                                    patente = patente,
                                    id_compania = id_compania,
                                    usuario_alta = current_user.username)
        
        estado.solicitudes.append(nueva_solicitud) 
        estado.save()

        flash("La solicitud se ha guardado correctamente.", "alert-success")
        
        return redirect(url_for("operaciones.alta_solicitudes"))
    

    return render_template("operaciones/alta_solicitudes.html", form = form)
