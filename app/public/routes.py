
import logging
import os

from flask import abort, render_template, redirect, url_for, request, current_app, flash
from flask_login import current_user

#from app.models import Post, Comment
from . import public_bp
# from .forms import CommentForm, UploadForm
from werkzeug.utils import secure_filename
from datetime import datetime
import json
logger = logging.getLogger(__name__)


@public_bp.route("/", methods = ['GET', 'POST'])
def index():
    #controlo asi porque no tengo form
    if request.method == 'POST':
        archivo = request.files.get('foto')
        metadatos_json = request.form.get('metadatos')

        if archivo:
            # Si querés pasar un nombre sugerido en la URL (opcional)
            nombre_archivo_variable = request.args.get('nombre_archivo_variable', '')

            # Si no viene, generás uno automáticamente
            if not nombre_archivo_variable:
                nombre_archivo_variable = f"foto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

            archivo_name = secure_filename(nombre_archivo_variable)
            archivo_dir = current_app.config.get('ARCHIVOS_DIR', 'uploads')
            os.makedirs(archivo_dir, exist_ok=True)
            file_path = os.path.join(archivo_dir, archivo_name)
            archivo.save(file_path)

            # Procesar metadatos si existen
            if metadatos_json:
                try:
                    metadatos = json.loads(metadatos_json)
                    print("Geolocalización:", metadatos.get('geolocalizacion'))
                    print("Fecha:", metadatos.get('fecha'))
                except Exception as e:
                    print("Error leyendo metadatos:", e)

            flash(f"Imagen guardada como {archivo_name}", "alert-success")
            return redirect(url_for("public.index"))

    return render_template("public/index.html")
      