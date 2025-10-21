import logging

from datetime import date, datetime, timedelta

from flask import render_template, redirect, url_for, abort, current_app, flash, request
from flask_login import login_required, current_user

from app.auth.decorators import admin_required, not_initial_status
from app.auth.models import Users
from app.models import  Estados, Personas, Solicitudes

from . import consultas_bp 
from .forms import BusquedaForm


logger = logging.getLogger(__name__)

def control_vencimiento (fecha):
    if fecha < datetime.now():
        return "VENCIDO"

@consultas_bp.route("/consultas/consultapersonas/", methods = ['GET', 'POST'])
@login_required
@not_initial_status
def consulta_personas():
    criterio = request.args.get('criterio','')

    form = BusquedaForm()
    lista_de_personas = []
    page = int(request.args.get('page', 1))
    per_page = current_app.config['ITEMS_PER_PAGE']
    if form.validate_on_submit():
        buscar = form.buscar.data
        return redirect(url_for("consultas.consulta_personas", criterio = buscar))
    if criterio.isdigit() == True:
        lista_de_personas = Personas.get_by_cuit(criterio)
    elif criterio == "":
        pass
    else:
        lista_de_personas = Personas.get_like_descripcion_all_paginated(criterio, page, per_page)
        if len(lista_de_personas.items) == 0:
            lista_de_personas =[]

    return render_template("consultas/consulta_personas.html", form = form, criterio = criterio, lista_de_personas= lista_de_personas )

@consultas_bp.route("/consultas/consultasolicitudes/", methods = ['GET', 'POST'])
@login_required
@not_initial_status
def consulta_solicitudes():
    solicitudes = Solicitudes.get_all()
    page = int(request.args.get('page', 1))
    per_page = current_app.config['ITEMS_PER_PAGE']


    return render_template("consultas/consulta_solicitudes.html", solicitudes= solicitudes )

