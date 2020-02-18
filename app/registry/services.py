from app.models import Registry, Access, Group
from flask_login import current_user
from sqlalchemy import or_
from app import db
from flask import current_app


def get_registries():
    role = current_user.role.name
    group_ids = [g.id for g in current_user.groups]
    if role == 'super':
        return Registry.query.all()
    else:
        return Registry.query.filter(
            or_(Registry.access.has(Access.name == 'all'), Registry.groups.any(Group.id.in_(group_ids)),
                Registry.creator_id == current_user.id)).all()


def add_registry(form):
    try:
        registry = Registry()
        registry.name = form.name.data
        registry.url = form.url.data
        registry.access_id = form.access.data
        registry.groups = Group.query.filter(Group.id.in_(form.groups.data)).all()
        registry.creator_id = current_user.id
        db.session.add(registry)
        db.session.commit()
        return registry
    except Exception as ex:
        current_app.logger.error(ex)
        return None


def update_registry(registry_id, form):
    try:
        registry = Registry.query.get(registry_id)
        registry.name = form.name.data
        registry.url = form.url.data
        registry.access_id = form.access.data
        registry.groups = Group.query.filter(Group.id.in_(form.groups.data)).all()
        db.session.commit()
        return registry
    except Exception as ex:
        current_app.logger.error(ex)
        return None


def remove_registry(ids):
    try:
        registries = Registry.query.filter(Registry.id.in_(ids))
        for registry in registries:
            db.session.delete(registry)
        db.session.commit()
        return []
    except Exception as ex:
        current_app.logger.error(ex)
        return ids
