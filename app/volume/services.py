from app.models import Group, Volume, Endpoint, Access
from flask_login import current_user
from app.utils.docker import docker_client
from docker.errors import DockerException, APIError
from sqlalchemy import or_, and_


def get_volumes(endpoint_id):
    role = current_user.role.name
    endpoint = Endpoint.query.get(endpoint_id)
    try:
        client = docker_client(endpoint.url)
    except (DockerException, APIError) as ex:
        return []
    volumes_in_docker = client.volumes.list()
    group_ids = [g.id for g in current_user.groups]
    if role == 'super':
        volumes_in_db_dict = volume_query_to_dict(Volume.query.with_entities(Volume.volume_hash, Volume).all())
        volumes_exclude_ids = []
        reverse = False
    elif role == 'group':
        volumes_in_db_dict = volume_query_to_dict(Volume.query.with_entities(Volume.volume_hash, Volume)
                                                  .filter(or_(Volume.access.has(Access.name == 'all'),
                                                              and_(Volume.access.has(Access.name == 'group'),
                                                                   Volume.groups.any(Group.id.in_(group_ids))),
                                                              Volume.creator_id == current_user.id))
                                                  .all())
        volumes_exclude_ids = Volume.query.with_entities(Volume.volume_hash).filter(
            or_(Volume.access.has(Access.name == 'none'),
                and_(Volume.access.has(Access.name == 'group'),
                     Volume.groups.any(~Group.id.in_(group_ids))))).all()
        reverse = False
    else:
        volumes_in_db_dict = volume_query_to_dict(Volume.query.with_entities(Volume.volume_hash, Volume)
                                                  .filter(or_(Volume.access.has(Access.name == 'all'),
                                                              and_(Volume.access.has(Access.name == 'group'),
                                                                   Volume.groups.any(Group.id.in_(group_ids))),
                                                              Volume.creator_id == current_user.id))
                                                  .all())
        volumes_exclude_ids = []
        reverse = True
    volumes_in_docker = merge_volume_info(volumes_in_docker, volumes_in_db_dict, volumes_exclude_ids, reverse)
    return volumes_in_docker


def merge_volume_info(volumes_in_docker, volumes_in_db_dict, volumes_exclude_ids=(), reverse=False):
    new_volumes_in_docker = []
    for volume in volumes_in_docker:
        if volume.attrs['Id'] in volumes_exclude_ids or (reverse and volume.attrs['Id'] not in volumes_in_db_dict):
            continue
        if volume.attrs['Id'] in list(volumes_in_db_dict.keys()):
            volume.is_in_db = True
            volume.creator = volumes_in_db_dict[volume.attrs['Id']].creator.username
            volume.action = volumes_in_db_dict[volume.attrs['Id']].creator_id == current_user.id
        else:
            volume.is_in_db = False
            volume.creator = ''
            volume.action = current_user.role.name == 'super'
        new_volumes_in_docker.append(volume)
    return new_volumes_in_docker


def volume_query_to_dict(volumes_list):
    volumes_dict = dict()
    for k, v in volumes_list:
        volumes_dict[k] = v
    return volumes_dict
