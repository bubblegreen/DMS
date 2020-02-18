from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from time import time
from app import db, login
import jwt
from flask import current_app
from sqlalchemy.exc import OperationalError

user2group = db.Table('user2group',
                      db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                      db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True))

user2permission = db.Table('user2permission',
                           db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                           db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'), primary_key=True))

image2group = db.Table('image2group',
                       db.Column('image_id', db.Integer, db.ForeignKey('image.id'), primary_key=True),
                       db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True))

container2group = db.Table('container2group',
                           db.Column('container_id', db.Integer, db.ForeignKey('container.id'), primary_key=True),
                           db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True))

volume2group = db.Table('volume2group',
                        db.Column('volume_id', db.Integer, db.ForeignKey('volume.id'), primary_key=True),
                        db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True))

network2group = db.Table('network2group',
                         db.Column('network_id', db.Integer, db.ForeignKey('network.id'), primary_key=True),
                         db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True))

endpoint2group = db.Table('endpoint2group',
                          db.Column('endpoint_id', db.Integer, db.ForeignKey('endpoint.id'), primary_key=True),
                          db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True))

registry2group = db.Table('registry2group',
                          db.Column('registry', db.Integer, db.ForeignKey('registry.id'), primary_key=True),
                          db.Column('group', db.Integer, db.ForeignKey('group.id'), primary_key=True))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    # name = db.Column(db.String(64))
    password_hash = db.Column(db.String(128), nullable=False)
    create_date = db.Column(db.DateTime, default=db.func.now())
    last_visit = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    active = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), default=3)
    role = db.relationship("Role", foreign_keys='User.role_id', uselist=False)
    groups = db.relationship('Group', secondary=user2group, backref=db.backref('members'))
    permissions = db.relationship('Permission', secondary=user2permission)
    images = db.relationship('Image', backref='creator')
    containers = db.relationship('Container', backref='creator')
    volumes = db.relationship('Volume', backref='creator')
    networks = db.relationship('Network', backref='creator')
    endpoints = db.relationship('Endpoint', backref='creator')
    registries = db.relationship('Registry', backref='creator')

    @property
    def username(self):
        return self.email[:self.email.index('@')]

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return self.active == 1

    @property
    def permission_info(self):
        permissions = {}
        for permission in self.permissions:
            permissions[permission.name] = permission
        return permissions

    def get_id(self):
        return str(self.id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        db.session.commit()

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def activate(self):
        self.active = True
        db.session.commit()

    def inactivate(self):
        self.active = False
        db.session.commit()

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    def get_register_confirm_token(self):
        return jwt.encode(
            {'register_confirm': self.id},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            user_id = jwt.decode(token, current_app.config['SECRET_KEY'],
                                 algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(user_id)

    @staticmethod
    def verify_register_confirm_token(token):
        try:
            user_id = jwt.decode(token, current_app.config['SECRET_KEY'],
                                 algorithms=['HS256'])['register_confirm']
            print(user_id)
        except:
            return
        return User.query.get(user_id)


@login.user_loader
def load_user(user_id):
    try:
        user = User.query.get(int(user_id))
        return user
    except OperationalError as ex:
        current_app.logger.error(ex)
        return None


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(140), nullable=False)

    def __repr__(self):
        return '<role {}>'.format(self.name, )


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    desc = db.Column(db.String(255), nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = relationship('User', foreign_keys='Group.creator_id', uselist=False)
    create_time = db.Column(db.DateTime, default=db.func.now())
    active = db.Column(db.Boolean, default=True)


class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), index=True)
    permission_type = db.Column('type', db.String(20))
    value = db.Column(db.Integer)


class Access(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hash = db.Column(db.String(255), nullable=False, unique=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    create_time = db.Column(db.DateTime, default=db.func.now())
    access_id = db.Column(db.Integer, db.ForeignKey('access.id'), nullable=False)
    access = db.relationship('Access', foreign_keys='Image.access_id', uselist=False)
    groups = db.relationship('Group', secondary=image2group, backref=db.backref('images'))


class Container(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hash = db.Column(db.String(255), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    create_time = db.Column(db.DateTime, default=db.func.now())
    access_id = db.Column(db.Integer, db.ForeignKey('access.id'), nullable=False)
    access = db.relationship('Access', foreign_keys='Container.access_id', uselist=False)
    groups = db.relationship('Group', secondary=container2group, backref=db.backref('containers'))


class Volume(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hash = db.Column(db.String(255), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    create_time = db.Column(db.DateTime, default=db.func.now())
    access_id = db.Column(db.Integer, db.ForeignKey('access.id'), nullable=False)
    access = db.relationship('Access', foreign_keys='Volume.access_id', uselist=False)
    groups = db.relationship('Group', secondary=volume2group, backref=db.backref('volumes'))


class Network(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hash = db.Column(db.String(255), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    create_time = db.Column(db.DateTime, default=db.func.now())
    access_id = db.Column(db.Integer, db.ForeignKey('access.id'), nullable=False)
    access = db.relationship('Access', foreign_keys='Network.access_id', uselist=False)
    groups = db.relationship('Group', secondary=network2group, backref=db.backref('networks'))


class Endpoint(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(100), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    create_time = db.Column(db.DateTime, default=db.func.now())
    access_id = db.Column(db.Integer, db.ForeignKey('access.id'), nullable=False)
    access = db.relationship('Access', foreign_keys='Endpoint.access_id', uselist=False)
    groups = db.relationship('Group', secondary=endpoint2group, backref=db.backref('endpoints'))


class Registry(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(100), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    create_time = db.Column(db.DateTime, default=db.func.now())
    access_id = db.Column(db.Integer, db.ForeignKey('access.id'), nullable=False)
    access = db.relationship('Access', foreign_keys='Registry.access_id', uselist=False)
    groups = db.relationship('Group', secondary=registry2group, backref=db.backref('registries'))
