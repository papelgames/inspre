import logging

from datetime import date, datetime, timedelta

from flask import render_template, redirect, url_for, abort, current_app, flash, request, make_response
from flask_login import login_required, current_user

from app.auth.decorators import admin_required, not_initial_status
from app.auth.models import Users
from app.models import  Estados, Personas, Solicitudes

from . import consultas_bp 
from .forms import BusquedaForm
from weasyprint import HTML

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

@consultas_bp.route("/consultas/report/", methods = ['GET', 'POST'])
def generar_reporte_pdf():
    numero_solicitud = request.args.get('numero_solicitud','')
    # Obtener datos
    solicitud = Solicitudes.get_all_by_solcitud(numero_solicitud)
    archivo_dir = current_app.config.get('ARCHIVOS_DIR', 'uploads')
    # Renderizar HTML con tu plantilla
    html_string = render_template('consultas/reporte.html', 
                                  solicitud=solicitud, archivo_dir=archivo_dir, fotos_por_pagina=6)
    
    # Convertir a PDF
    pdf = HTML(string=html_string).write_pdf()
    
    # Crear respuesta
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=reporte_{numero_solicitud}.pdf'
    
    return response