
import logging
import os

from flask import abort, render_template, redirect, url_for, request, current_app, flash
from flask_login import current_user

from app.models import Nodos, TiposVehiculos, Fotos, Solicitudes
from . import public_bp
# from .forms import CommentForm, UploadForm
from werkzeug.utils import secure_filename
from datetime import datetime
import json
logger = logging.getLogger(__name__)


@public_bp.route("/inspeccion", methods = ['GET', 'POST'])
def inspeccion():
    tipo_vehiculo = request.args.get('tipo_vehiculo','')
    solicitud = request.args.get('solicitud','')
    page = int(request.args.get('page', 1))
    id_tipo_vehiculo = TiposVehiculos.get_id_by_clave(tipo_vehiculo)
    nodos_x_tipo_vehiculo = Nodos.get_nodos_by_id_tipo_vehiculo_all_paginated(id_tipo_vehiculo.id, page)
    
    id_solcitud = Solicitudes.get_id_by_solcitud(solicitud)

    for id_nodo in nodos_x_tipo_vehiculo.items: 
        #controlo asi porque no tengo form
        if request.method == 'POST':
            archivo = request.files.get('foto')
            metadatos_json = request.form.get('metadatos')

            if archivo:
                # Si querés pasar un nombre sugerido en la URL (opcional)
                nombre_archivo_variable = request.args.get('nombre_archivo_variable', '')

                # Si no viene, generás uno automáticamente
                if not nombre_archivo_variable:
                    nombre_archivo_variable = f"{id_nodo.nombre}-id_s{id_solcitud.id}-id_n{id_nodo.id}-{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

                archivo_name = secure_filename(nombre_archivo_variable)
                archivo_dir = current_app.config.get('ARCHIVOS_DIR', 'uploads')
                os.makedirs(archivo_dir, exist_ok=True)
                file_path = os.path.join(archivo_dir, archivo_name)
                archivo.save(file_path)

                # Procesar metadatos si existen
                if metadatos_json:
                    try:
                        metadatos = json.loads(metadatos_json)
                        fecha_md = datetime.strptime(metadatos.get('fecha'), '%d/%m/%Y, %H:%M:%S')
                        plataforma_md = metadatos.get('plataforma')
                        latitud_md = metadatos.get('geolocalizacion').get('latitud')
                        longitud_md = metadatos.get('geolocalizacion').get('longitud')
                        precision_md = metadatos.get('geolocalizacion').get('precision')
                        camara_md = metadatos.get('camaraUsada')
                    except Exception as e:
                        print("Error leyendo metadatos:", e)

                nueva_foto = Fotos(nombre = archivo_name,
                                fecha_hora = fecha_md,
                                nombre_celular = plataforma_md,
                                latitud = latitud_md,
                                longitud = longitud_md,
                                precision = precision_md,
                                camara = camara_md)

                id_nodo.fotos.append(nueva_foto)   
                id_nodo.save()      
                id_solcitud.fotos.append(nueva_foto)
                id_solcitud.save()

    
                flash("Imagen guardada correctamente", "alert-success")
                return redirect(url_for('public.inspeccion', solicitud=solicitud,tipo_vehiculo=tipo_vehiculo, page=page+1) )

    return render_template("public/inspeccion.html", nodos_x_tipo_vehiculo=nodos_x_tipo_vehiculo, solicitud=solicitud, tipo_vehiculo=tipo_vehiculo)

@public_bp.route("/")
def index():
    return render_template("public/index.html")
