from app.models import User, Permission, Role
from app import db


def set_default_permission(user):
    role_name = user.role.name
    if role_name == 'super':
        permission_lst = __get_super_default_permission()
    elif role_name == 'group':
        permission_lst = __get_group_default_permission()
    else:
        permission_lst = __get_norm_default_permission()
    user.permissions = list(permission_lst)
    db.session.commit()


def set_user_role(user, role_name):
    role = Role.query.filter(Role.name == role_name).first()
    user.role = role
    set_default_permission(user)


def set_user_permission(user, permission_dict):
    permission_list = []
    for k, v in permission_dict:
        permission = Permission.query.filter(Permission.name == k).filter(Permission.permission_type == v).first()
        if permission is not None:
            permission_list.append(permission)
    user.permissions = permission_list
    db.session.commit()


def __get_norm_default_permission():
    image_pm = Permission.query.filter(Permission.name == 'image' and Permission.permission_type == 'view').first()
    container_pm = Permission.query.filter(
        Permission.name == 'container' and Permission.permission_type == 'view').first()
    network_pm = Permission.query.filter(Permission.name == 'network' and Permission.permission_type == 'view').first()
    volume_pm = Permission.query.filter(Permission.name == 'volume' and Permission.permission_type == 'view').first()
    endpoint_pm = Permission.query.filter(
        Permission.name == 'endpoint' and Permission.permission_type == 'view').first()
    return image_pm, container_pm, network_pm, volume_pm, endpoint_pm


def __get_group_default_permission():
    image_pm = Permission.query.filter(Permission.name == 'image' and Permission.permission_type == 'create').first()
    container_pm = Permission.query.filter(
        Permission.name == 'container' and Permission.permission_type == 'create').first()
    network_pm = Permission.query.filter(
        Permission.name == 'network' and Permission.permission_type == 'create').first()
    volume_pm = Permission.query.filter(Permission.name == 'volume' and Permission.permission_type == 'create').first()
    endpoint_pm = Permission.query.filter(
        Permission.name == 'endpoint' and Permission.permission_type == 'view').first()
    return image_pm, container_pm, network_pm, volume_pm, endpoint_pm


def __get_super_default_permission():
    image_pm = Permission.query.filter(Permission.name == 'image' and Permission.permission_type == 'create').first()
    container_pm = Permission.query.filter(
        Permission.name == 'container' and Permission.permission_type == 'create').first()
    network_pm = Permission.query.filter(
        Permission.name == 'network' and Permission.permission_type == 'create').first()
    volume_pm = Permission.query.filter(Permission.name == 'volume' and Permission.permission_type == 'create').first()
    endpoint_pm = Permission.query.filter(
        Permission.name == 'endpoint' and Permission.permission_type == 'create').first()
    return image_pm, container_pm, network_pm, volume_pm, endpoint_pm
