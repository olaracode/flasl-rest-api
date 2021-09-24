"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, Usuario, Plant
from functools import wraps
import jwt, datetime, time
import cloudinary.uploader as uploader

#from models import Person

secret = 'jwt_secret_key'

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SECRET_KEY'] = secret
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config.from_mapping(
    CLOUDINARY_URL=os.environ.get('CLOUDINARY_URL')
)
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)


def autenticacion(func):
    @wraps(func)
    def decorador(*args, **kwargs):
        token = None

        if 'token-acceso' in request.headers:
            token = request.headers['token-acceso']
        if not token:
            return jsonify({'mensaje': 'Se necesita un token de acceso valido'})
        try:  
            data = jwt.decode(token, options={"verify_signature": False})
            autentificacionUsuario = Usuario.query.filter_by(id=data['id']).first()  
        except:  
            return jsonify({'mensaje': 'Token invalido'})  
        return func(autentificacionUsuario, *args,  **kwargs)  
    return decorador 
# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/usuario/crear', methods=['POST'])
#Decorador (ruta, metodo)
def crear_usuario():
#    nombre de la funcion
#    solicitud parametro 
    nombre = request.json["nombre"]
    correo = request.json["correo"]
    clave = request.json["clave"]
    #Se encripta la contraseña
    claveEncriptada = generate_password_hash(clave, method='sha256')
    nuevo_usuario= Usuario(nombre=nombre, correo=correo, clave=claveEncriptada) 
    # crear nuevo con el clase Usuario
    db.session.add(nuevo_usuario)
    #agregar a la bd el nuevo usuario
    db.session.commit()
    #guardar en la bd el nuevo usuario
    return jsonify(nuevo_usuario.serialize())
#retorna, jsonify convierte en Json la respuesta y serialize pasa todos los campos del modelo dezglosa.

@app.route('/usuario/profile', methods=['GET'])
@autenticacion
def perfilUsuario(user_auth):
    usuario = Usuario.query.get(user_auth.id)
    return jsonify(usuario.serialize())

@app.route('/usuario/', methods=['PUT'])
@autenticacion
def actualizar_usuario(user_auth):
    usuario_obtenido= Usuario.query.get(user_auth.id)
    usuario_obtenido.nombre = request.json["nombre"]
    usuario_obtenido.correo = request.json["correo"]
    usuario_obtenido.clave = request.json["clave"]
    
    db.session.commit()
    return jsonify(usuario_obtenido.serialize())

@app.route('/usuario/', methods=['DELETE'])
@autenticacion
def Borrar_usuario(user_auth):
    usuario_obtenido= Usuario.query.get(user_auth.id)
    
    db.session.delete(usuario_obtenido)
    db.session.commit()
    return jsonify({ "message": 'Usuario eliminado satisfactoriamente'})


@app.route('/usuario/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data['correo'] or not data['clave']:
        return make_response({'Se necesita nombre y clave', 401})
    usuario = Usuario.query.filter_by(correo=data['correo']).first()
    if check_password_hash(usuario.clave, data["clave"]):
        token = jwt.encode({'id': usuario.id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token})
    return make_response('Verifique sus datos', 401)

@app.route('/plant/crear/', methods=['POST'])
@autenticacion
def crearPerro(user_auth):
    tipo=request.json["tipo"]
    le=request.json["le"]
    hrs=request.json["hrs"]
    nuevaPlanta = Plant(
        usuario_id=user_auth.id, 
        tipo=tipo,
        le=le,
        hrs=hrs,)
    db.session.add(nuevaPlanta)
    db.session.commit()
    return jsonify({'mensaje': 'Planta creada con exito'})

@app.route('/plant/<id>', methods=['GET'])
@autenticacion
def plant(user_auth, id):
    plantActual = Plant.query.get(id)
    return jsonify(plantActual.serialize())


@app.route('/usuario/plants', methods=['GET'])
@autenticacion
def perrosUsuario(user_auth):
    userPlants = [plant.serialize() for plant in Plant.query.filter_by(usuario_id=user_auth.id).all()]
    return jsonify({'userPlants': userPlants})

@app.route('/plant/<id>', methods=['DELETE'])
@autenticacion
def Borrar_planta(user_auth, id):
    plant= Plant.query.get(id)
    
    db.session.delete(plant)
    db.session.commit()
    return jsonify({ "message": 'Planta eliminada con exito'})


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
