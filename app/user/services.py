from app.models import Group, User, Permission
from flask import current_app
from flask_login import current_user
from app import db


def get_all_users():
    role = current_user.role.name
    if role == 'super':
        users = User.query.filter(User.active).all()
    else:
        group_ids = [g.id for g in current_user.groups]
        users = User.query.filter(User.active).filter(User.groups.any(Group.id.in_(group_ids))).all()
    return users


def get_all_users_with_inactive():
    role = current_user.role.name
    if role == 'super':
        users = User.query.all()
    else:
        group_ids = [g.id for g in current_user.groups]
        users = User.query.filter(User.groups.any(Group.id.in_(group_ids))).all()
    return users


def update_user(user_id, form):
    try:
        user = User.query.get(user_id)
        if form.password.data != '':
            user.set_password(form.password.data)
        if user.role_id != 1:
            user.role_id = form.role.data
        user.groups = Group.query.filter(Group.id.in_(form.groups.data)).all()
        permissions = []
        if form.image_permission.data != 0:
            permissions.append(Permission.query.get(form.image_permission.data))
        if form.container_permission.data != 0:
            permissions.append(Permission.query.get(form.container_permission.data))
        if form.network_permission.data != 0:
            permissions.append(Permission.query.get(form.network_permission.data))
        if form.volume_permission.data != 0:
            permissions.append(Permission.query.get(form.volume_permission.data))
        if form.endpoint_permission.data != 0:
            permissions.append(Permission.query.get(form.endpoint_permission.data))
        user.permissions = permissions
        db.session.commit()
        return user
    except Exception as ex:
        current_app.logger.error(ex)
        return None


def change_user_active(ids):
    try:
        users = User.query.filter(User.id.in_(ids))
        for user in users:
            user.active = not user.active
        db.session.commit()
        return 'ok'
    except Exception as ex:
        current_app.logger.error(ex)
        return None
