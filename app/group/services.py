from app.models import Group, User, Access
from flask import current_app
from flask_login import current_user
from app import db


def get_all_groups():
    role = current_user.role.name
    if role == 'super':
        groups = Group.query.filter(Group.active).all()
    else:
        groups = Group.query.filter(Group.active).filter(Group.creator.has(User.id == current_user.id)).all()
    return groups


def get_all_groups_with_inactive():
    role = current_user.role.name
    if role == 'super':
        groups = Group.query.all()
    else:
        groups = Group.query.filter(Group.creator.has(User.id == current_user.id)).all()
    return groups


def add_group(form):
    try:
        group = Group()
        group.name = form.name.data
        group.desc = form.desc.data
        group.creator_id = current_user.id
        group.members = User.query.filter(User.id.in_(form.members.data)).all()
        db.session.add(group)
        db.session.commit()
        return group
    except Exception as ex:
        current_app.logger.error(ex)
        return None


def update_group(group_id, form):
    try:
        group = Group.query.get(group_id)
        group.name = form.name.data
        group.desc = form.desc.data
        group.members = User.query.filter(User.id.in_(form.members.data)).all()
        db.session.commit()
        return group
    except Exception as ex:
        current_app.logger.error(ex)
        return None


def remove_group(ids):
    try:
        groups = Group.query.filter(Group.id.in_(ids))
        for group in groups:
            group.active = False
        db.session.commit()
        return []
    except Exception as ex:
        current_app.logger.error(ex)
        return ids
