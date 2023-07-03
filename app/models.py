from datetime import datetime
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
from flask_security import RoleMixin
from flask_login import UserMixin

"""roles_users_table = db.Table('roles_users',
    db.Column('users_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))"""


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    active = db.Column(db.Boolean())

    role = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)

    interventions = db.relationship('Intervention', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return True
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)
    

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.Text())

    users = db.relationship('User', backref='active_role', lazy=True)

    def __repr__(self):
        return f'<Role {self.name}>'


class Machine(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    manufacturer = db.Column(db.String(64))
    location = db.Column(db.String(64))
    status = db.Column(db.String(12))
    install_date = db.Column(db.DateTime(), index=True)
    comment = db.Column(db.String(255))

    documents = db.relationship('Document', backref='machine', lazy=True)

    interventions = db.relationship('Intervention', backref='machine', lazy=True)

    def __repr__(self):
        return f'<Machine {self.id}>'


class Document(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    machine_id = db.Column(db.Integer, db.ForeignKey('machine.id'), nullable=False)
    type = db.Column(db.String(12))
    upload_date = db.Column(db.DateTime(), index=True)
    blob = db.Column(db.LargeBinary(), nullable=False)
    size = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Document {self.id}>'

class Intervention(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    machine_id = db.Column(db.Integer, db.ForeignKey('machine.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(12))
    comment = db.Column(db.String(255))
    start_date = db.Column(db.DateTime(), index=True)
    end_date = db.Column(db.DateTime(), index=True)

    def __repr__(self):
        return f'<Intervention {self.id}>'
    
@login.user_loader
def load_user(id):
    return User.query.get(int(id))