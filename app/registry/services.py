from app.models import Registry, Access, Group
from flask_login import current_user
from sqlalchemy import or_


def get_registries():
    role = current_user.role.name
    group_ids = [g.id for g in current_user.groups]
    if role == 'super':
        return Registry.query.all()
    else:
        return Registry.query.filter(
            or_(Registry.access.has(Access.name == 'all'), Registry.groups.any(Group.id.in_(group_ids)))).all()
