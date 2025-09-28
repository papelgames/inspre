
import datetime
from email.policy import default
from itertools import product
from types import ClassMethodDescriptorType
from typing import Text

#from slugify import slugify
from sqlalchemy import func, or_, alias, not_
from sqlalchemy.orm import aliased
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
#from app.auth.models import Users

from app import db

class Base(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=db.func.current_timestamp())
    modified = db.Column(db.DateTime, default=db.func.current_timestamp(),\
                     onupdate=db.func.current_timestamp())

class Personas (Base):
    __tablename__ = "personas"
    descripcion_nombre = db.Column(db.String(50), nullable = False)
    cuit = db.Column(db.String(11), nullable = False)
    dni = db.Column(db.String(8), nullable = False)
    correo_electronico = db.Column(db.String(256))
    telefono = db.Column(db.String(256))
    genero = db.Column(db.String(9))
    fecha_nacimiento = db.Column(db.DateTime)
    tipo_persona = db.Column(db.String(50))
    id_estado = db.Column(db.Integer, db.ForeignKey('estados.id'))
    direccion = db.Column(db.String(256))
    nota = db.Column(db.String(256))
    usuario_alta = db.Column(db.String(256))
    usuario_modificacion = db.Column(db.String(256))
    id_usuario = db.Column(db.Integer, db.ForeignKey('users.id'))

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.flush()
        db.session.commit()

    @staticmethod
    def get_all():
        return Personas.query.all()
    
    @staticmethod
    def get_by_id(id_persona):
        return Personas.query.filter_by(id = id_persona).first()
    
    @staticmethod
    def get_by_cuit(cuit):
        return Personas.query.filter_by(cuit = cuit).first()

    @staticmethod
    def get_by_correo(correo):
        return Personas.query.filter_by(correo_electronico = correo).first()
        
    @staticmethod
    def get_like_descripcion_all_paginated(descripcion_, page=1, per_page=20):
        descripcion_ = f"%{descripcion_}%"
        return db.session.query(Personas)\
            .filter(Personas.descripcion_nombre.contains(descripcion_))\
            .paginate(page=page, per_page=per_page, error_out=False)
 
class Estados(Base):
    __tablename__ = "estados"
    clave = db.Column(db.Integer)
    descripcion = db.Column(db.String(50))
    tabla = db.Column(db.String(50))
    inicial = db.Column(db.Boolean)
    final = db.Column(db.Boolean)
    usuario_alta = db.Column(db.String(256))
    usuario_modificacion = db.Column(db.String(256))
    personas = db.relationship('Personas', backref='estado_personas', uselist=True)
    users = db.relationship('Users', backref='estado_users', uselist=True)
    nodos = db.relationship('Nodos', backref='estado_nodo', uselist=True)
    solicitudes = db.relationship('Solicitudes', backref='estado_solicitud', uselist=True)
   
    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Estados.query.all()
    
    @staticmethod
    def get_first_by_clave_tabla(clave, tabla):
        return Estados.query.filter_by(clave = clave, tabla = tabla).first()

class PermisosPorUsuarios(Base):
    __tablename__ = "permisosporusuarios"
    id_permiso = db.Column(db.Integer, db.ForeignKey('permisos.id'))
    id_usuario = db.Column(db.Integer, db.ForeignKey('users.id'))

class Roles(Base):
    __tablename__ = "roles"
    descripcion = db.Column(db.String(50))
    usuario_alta = db.Column(db.String(256))
    usuario_modificacion = db.Column(db.String(256))
    permisos = db.relationship('Permisos', secondary='permisosenroles', back_populates='roles')

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    @staticmethod
    def get_by_id(id):
        return Roles.query.get(id)

    @staticmethod
    def get_all_by_id(id):
        return Roles.query.filter_by(id = id).all()
    
    @staticmethod
    def get_all():
        return Roles.query.all()

    @staticmethod
    def get_all_descripcion_agrupada():
        return db.session.query(Roles.descripcion.label('nombre_rol')).distinct().all()

class PermisosEnRoles(Base):
    __tablename__ = "permisosenroles"
    id_permiso = db.Column(db.Integer, db.ForeignKey('permisos.id'))
    id_roles =db.Column(db.Integer, db.ForeignKey('roles.id'))

class Permisos(Base):
    __tablename__ = "permisos"
    descripcion = db.Column(db.String(50))
    roles = db.relationship('Roles', secondary='permisosenroles', back_populates='permisos')
    users = db.relationship('Users', secondary='permisosporusuarios', back_populates='permisos')
    usuario_alta = db.Column(db.String(256))
    usuario_modificacion = db.Column(db.String(256))

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()
    
    def save_masivo(self, lista):
        db.session.bulk_save_objects(lista)
        db.session.commit()
    
    @staticmethod
    def get_all():
        return Permisos.query.all()

    @staticmethod
    def get_by_id(id_permiso):
        return Permisos.query.filter_by(id = id_permiso).first()

    @staticmethod
    def get_by_descripcion(descripcion):
        return Permisos.query.filter_by(descripcion = descripcion).first()

    @staticmethod
    def get_permisos_no_relacionadas_roles(id_rol): 
        return  Permisos.query.filter(~Permisos.roles.any(id = id_rol)).all()
    
    @staticmethod
    def get_permisos_no_relacionadas_personas(id_persona): 
        return  Permisos.query.filter(~Permisos.users.any(id = id_persona)).all()
  
class Companias(Base):
    __tablename__ = "companias"
    id_ssn = db.Column(db.Integer)
    nombre_compania = db.Column(db.String(50))
    usuario_alta = db.Column(db.String(256))
    usuario_modificacion = db.Column(db.String(256))
    correo_electronico = db.Column(db.String(256))
    solicitudes = db.relationship('Solicitudes', backref='compania', uselist=True)

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Companias.query.all()

class Solicitudes (Base):
    __tablename__ = "solicitudes"
    nombre_asegurado = db.Column(db.String(50))
    vehiculo = db.Column(db.String(60))
    numero_riesgo = db.Column(db.Integer)
    solicitud = db.Column(db.BigInteger)
    patente = db.Column(db.String(7))
    id_compania = db.Column(db.Integer, db.ForeignKey('companias.id'))
    id_estado = db.Column(db.Integer, db.ForeignKey('estados.id'))
    usuario_alta = db.Column(db.String(256))
    usuario_modificacion = db.Column(db.String(256))
    fotos = db.relationship('Fotos', backref='solicitud', uselist=True)

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

class Fotos(Base):
    __tablename__ = "fotos"
    fecha_hora = db.Column(db.DateTime)
    nombre_celular = db.Column(db.String(50))
    geolocalizacion = db.Column(db.String(100))
    id_solicitud = db.Column(db.Integer, db.ForeignKey('solicitudes.id'))
    id_nodo = db.Column(db.Integer, db.ForeignKey('nodos.id'))

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()


class Nodos(Base):
    __tablename__ = "nodos"
    orden = db.Column(db.Integer)
    nombre = db.Column(db.String(50))
    final = db.Column(db.Boolean)
    id_estado = db.Column(db.Integer, db.ForeignKey('estados.id'))
    id_tipo_vehiculo = db.Column(db.Integer, db.ForeignKey('tiposvehiculos.id'))
    fotos = db.relationship('Fotos', backref='nodo', uselist=True)

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

class TiposVehiculos(Base):
    __tablename__ = "tiposvehiculos"
    clave = db.Column(db.String(2))
    descripcion = db.Column(db.String(50))
    usuario_alta = db.Column(db.String(256))
    usuario_modificacion = db.Column(db.String(256))
    nodos = db.relationship('Nodos', backref='tipo_vehiculo', uselist=True)
