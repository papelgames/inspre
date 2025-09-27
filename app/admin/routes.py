import logging
import os

from flask import render_template, redirect, url_for, abort, current_app, flash, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.auth.decorators import admin_required, not_initial_status, nocache
from app.auth.models import Users
from app.models import  Permisos, Roles, Personas, Estados
from . import admin_bp
from .forms import UserAdminForm, PermisosUserForm, RolesUserForm, DatosPersonasForm, TiposForm, PermisosForm, RolesForm, PermisosSelectForm, EstadosForm

from app.common.funciones import listar_endpoints, renderizar_modelo_con_instancia


logger = logging.getLogger(__name__)

#creo una tupla para usar en el campo select del form que quiera que necesite los permisos
def permisos_select(user_id):
    permisos = Permisos.get_permisos_no_relacionadas_personas(user_id)
    select_permisos =[]
    for rs in permisos:
        sub_select_permisos = (str(rs.id), rs.descripcion)
        select_permisos.append(sub_select_permisos)
    return select_permisos

#creo una tupla para usar en el campo select del form que quiera que necesite los permisos
def permisos_en_roles_select(rol_id):
    permisos = Permisos.get_permisos_no_relacionadas_roles(rol_id)
    select_permisos =[]
    for rs in permisos:
        sub_select_permisos = (str(rs.id), rs.descripcion)
        select_permisos.append(sub_select_permisos)
    return select_permisos

#creo una tupla para usar en el campo select del form que quiera que necesite los roles
def roles_select():
    roles = Roles.get_all()
    select_rol =[( '','Seleccionar permiso')]
    for rs in roles:
        sub_select_rol = (str(rs.id), rs.descripcion)
        select_rol.append(sub_select_rol)
    return select_rol


@admin_bp.route("/admin/")
@login_required
@admin_required
@not_initial_status
def index():
    return render_template("admin/index.html")

@admin_bp.route("/admin/users/")
@login_required
@admin_required
@not_initial_status
def list_users():
    users = Users.get_all()
    return render_template("admin/users.html", users=users)


@admin_bp.route("/admin/user/", methods=['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def update_user_form():
    user_id = request.args.get('user_id','')
    
    # Aquí entra para actualizar un usuario existente
    user = Users.get_by_id(user_id)
    if user is None:
        logger.info(f'El usuario {user_id} no existe')
        abort(404)
    # Crea un formulario inicializando los campos con
    # los valores del usuario.
    form = UserAdminForm(obj=user)
    if form.validate_on_submit():
        # Actualiza los campos del usuario existente
        # user.is_admin = form.is_admin.data
        # user.es_dibujante = form.es_dibujante.data
        form.populate_obj(user)
        user.save()
        logger.info(f'Guardando el usuario {user_id}')
        return redirect(url_for('admin.list_users'))
    return render_template("admin/user_form.html", form=form, user=user)


@admin_bp.route("/admin/user/delete/", methods=['POST', ])
@login_required
@admin_required
@not_initial_status
def delete_user():
    user_id = request.args.get('user_id','')
    user = Users.get_by_id(user_id)
    logger.info(f'Se va a eliminar al usuario {user_id}')
    if user is None:
        logger.info(f'El usuario {user_id} no existe')
        abort(404)
    user.delete()
    logger.info(f'El usuario {user_id} ha sido eliminado')
    return redirect(url_for('admin.list_users'))

@admin_bp.route("/admin/asignacionpermisos/", methods=['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def asignacion_permisos():
    user_id = request.args.get('user_id','')
    # Aquí entra para actualizar un usuario existente
    user = Users.get_by_id(user_id)
    form = PermisosUserForm()
    form.id_permiso.choices = permisos_select(user_id)
    
    if form.validate_on_submit():
        permiso = Permisos.get_by_id(form.id_permiso.data)
        for permiso_en_user in user.permisos:
            if permiso_en_user.id == int(form.id_permiso.data):
                flash ('El usuario ya tiene el permiso', 'alert-warning')
                return redirect(url_for('admin.asignacion_permisos', user_id = user_id))
        user.permisos.append(permiso)
        user.save()
        
        flash ('Permiso asignado correctamente', 'alert-success')
        return redirect(url_for('admin.asignacion_permisos', user_id = user_id))
    return render_template("admin/permisos_usuarios.html", form=form, user=user)

@admin_bp.route("/admin/asignacionroles/", methods=['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def asignacion_roles():
    user_id = request.args.get('user_id','')
    # Aquí entra para actualizar un usuario existente
    user = Users.get_by_id(user_id)
    form = RolesUserForm()
    form.rol.choices = roles_select()
    
    if form.validate_on_submit():
        permisos_de_roles = Roles.get_by_id(form.rol.data)
        for permiso in permisos_de_roles.permisos:
            control = True
            for permiso_en_user in user.permisos:
                if permiso_en_user.id == permiso.id:
                    control = False
                
            if control:
                user.permisos.append(permiso)
              
        user.save()

        flash ('Permiso asignado correctamente', 'alert-success')
        return redirect(url_for('admin.asignacion_roles', user_id = user_id))
    return render_template("admin/roles_usuarios.html", form=form, user=user)


@admin_bp.route("/admin/eliminarpermisousuario/", methods=['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def eliminar_permiso_usuario():
    user_id = request.args.get('user_id','')
    id_permiso = request.args.get('id_permiso','')
    user = Users.get_by_id(user_id)
    permiso = Permisos.get_by_id(id_permiso)
    
    user.permisos.remove(permiso)
    user.save()
    flash ('Permiso eliminado correctamente', 'alert-success')
    return redirect(url_for('admin.asignacion_permisos', user_id = user_id))

@admin_bp.route("/admin/altapersonas/", methods = ['GET', 'POST'])
@login_required
@not_initial_status
@nocache
def alta_persona():
    form = DatosPersonasForm()                                                                                                                   
    
    if form.validate_on_submit():
        descripcion_nombre = form.descripcion_nombre.data
        correo_electronico = form.correo_electronico.data
        fecha_nacimiento =form.fecha_nacimiento.data
        telefono = form.telefono.data
        cuit = form.cuit.data
        tipo_persona = form.tipo_persona.data 
        genero=form.genero.data
        direccion=form.direccion.data
        

        nota = form.nota.data

        persona = Personas(descripcion_nombre= descripcion_nombre,
                           correo_electronico = correo_electronico,
                           fecha_nacimiento = fecha_nacimiento,
                           telefono = telefono,
                           dni = cuit[2:10],
                           cuit = cuit, 
                           tipo_persona = tipo_persona,
                           genero = genero,
                           direccion=direccion,
                           nota = nota,
                           usuario_alta = current_user.username)
        persona.save()
        flash("Se ha creado la persona correctamente.", "alert-success")
        return redirect(url_for('consultas.consulta_personas'))
    return render_template("admin/datos_persona.html", form = form)

@admin_bp.route("/admin/actualizacionpersona/", methods = ['GET', 'POST'])
@login_required
@not_initial_status
def actualizacion_persona():
    id_persona = request.args.get('id_persona','')
    persona = Personas.get_by_id(id_persona)
    
    form=DatosPersonasForm(obj=persona)
    
    if form.validate_on_submit():
        form.populate_obj(persona)
        localidad = form.id_localidad.data.split('|')
        
        persona.id_localidad = localidad[0].strip()
        persona.save()
        flash("Se ha actualizado la persona correctamente.", "alert-success")
        return redirect(url_for('consultas.consulta_personas'))
    return render_template("admin/datos_persona.html", form=form, persona=persona)


@admin_bp.route("/admin/altapermisos/", methods = ['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def alta_permiso():
    form = PermisosForm()
    permisos = Permisos.get_all()
    if form.validate_on_submit():
        permisos_obj = []
        
        for item in listar_endpoints(current_app):
            check_permiso = Permisos.get_by_descripcion(item.get('descripcion'))
            if not check_permiso:
                permiso = Permisos(**item)
                permisos_obj.append(permiso)
        if permisos_obj:
            q_altas = len(permisos_obj)
            permiso.save_masivo(permisos_obj)
            flash(f"Se han creado {q_altas} permisos", "alert-success")
        else:
            flash(f"No hay nuevos permisos", "alert-warning")
        return redirect(url_for('admin.alta_permiso'))

    return render_template("admin/alta_permisos.html", form=form, permisos=permisos)

@admin_bp.route("/admin/eliminarpermisos/", methods=['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def eliminar_permiso():
    id_permiso = request.args.get('id_permiso','')
    permiso = Permisos.get_by_id(id_permiso)
    permiso.delete()
    
    flash ('Permiso eliminado correctamente', 'alert-success')
    return redirect(url_for('admin.alta_permiso'))

@admin_bp.route("/admin/crearroles/", methods=['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def crear_roles():
    form = RolesForm()
    
    todos_los_roles = Roles.get_all()

    if form.validate_on_submit():
        rol = Roles(descripcion = form.descripcion.data.upper(),
                    usuario_alta = current_user.username
        )
        rol.save() 
        
        flash ('Rol creado correctamente', 'alert-success')
        return redirect(url_for('admin.crear_roles'))
    return render_template("admin/alta_roles.html", form=form, todos_los_roles=todos_los_roles)

@admin_bp.route("/admin/asignarpermisosroles/", methods=['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def asignar_permisos_roles():
    id_rol = request.args.get('id_rol','')
    permisos_en_rol = Roles.get_by_id(id_rol)
    
    form = PermisosSelectForm()
    form.id_permiso.choices=permisos_en_roles_select(id_rol)
    
    if form.validate_on_submit():
        permiso = Permisos.get_by_id(form.id_permiso.data)
        for permiso_en_rol in permisos_en_rol.permisos:
            if permiso_en_rol.id == int(form.id_permiso.data):
                flash ('El rol ya tiene el permiso', 'alert-warning')
                return redirect(url_for('admin.asignar_permisos_roles', id_rol = id_rol))    
        
        permisos_en_rol.permisos.append(permiso)
        permisos_en_rol.save()

        flash ('Permiso asignado correctamente del rol', 'alert-success')
        return redirect(url_for('admin.asignar_permisos_roles', id_rol = id_rol))
    return render_template("admin/alta_permisos_en_roles.html", form=form, permisos_en_rol=permisos_en_rol)

@admin_bp.route("/admin/eliminarpermisosroles/", methods=['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def eliminar_permisos_roles():
    id_rol = request.args.get('id_rol','')
    id_permiso = request.args.get('id_permiso','')
    rol = Roles.get_by_id(id_rol)
    permiso = Permisos.get_by_id(id_permiso)
    rol.permisos.remove(permiso)
    rol.save()  
    
    flash ('Permiso eliminado correctamente del rol', 'alert-success')
    return redirect(url_for('admin.asignar_permisos_roles', id_rol = id_rol))

@admin_bp.route("/admin/altaestados/", methods = ['GET', 'POST'])
@login_required
@admin_required
@not_initial_status
def alta_estados():
    form = EstadosForm()
    
    if form.validate_on_submit():
        clave = form.clave.data
        descripcion = form.descripcion.data
        tabla = form.tabla.data
        inicial = form.inicial.data
        final = form.final.data
        
        estado = Estados(clave=clave,
                         descripcion=descripcion,
                         tabla=tabla,
                         inicial=inicial,
                         final=final,
                         usuario_alta=current_user.username)
        
        estado.save()
        flash("Nuevo estado creado", "alert-success")
        return redirect(url_for('admin.alta_estados'))
    #falta paginar tareas
    estados = Estados.get_all()    
    return render_template("admin/alta_estados.html", form=form, estados=estados)
