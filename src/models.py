from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuario(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    nombre= db.Column(db.String(15), unique=False, nullable=False)
    correo= db.Column(db.String(50), unique=True, nullable=False)
    clave= db.Column(db.Text(120), unique=False, nullable=False)

    def __repr__(self):
        return '<usuario %r>' % self.nombreusuario

    def serialize(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "correo": self.correo,
            # do not serialize the password, its a security breach
        }
    

class Plant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    le = db.Column(db.Integer, nullable=False)
    hrs = db.Column(db.Integer, nullable=True)
    tipo = db.Column(db.String(60), nullable=False)
    def __repr__(self):
        return '<Perro %r>' % self.nombre

    def serialize(self):
        return {
            "id": self.id,
            "le": self.le,
            "hrs": self.hrs,
            "tipo": self.tipo
        }