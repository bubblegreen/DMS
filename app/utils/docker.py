import docker
from flask_login import current_user
from app.models import Group, Access
from sqlalchemy import or_, and_


def docker_client(url):
    return docker.DockerClient(base_url=url, version='auto', timeout=5)


def merge_info(in_docker, in_db_dict, exclude_ids=(), reverse=False):
    new_in_docker = []
    keys = list(in_db_dict.keys())
    for entity in in_docker:
        if entity.id in exclude_ids or (reverse and entity.id not in in_db_dict):
            continue
        if entity.id in keys:
            entity.is_in_db = True
            entity.creator = in_db_dict[entity.id].creator.username
            entity.action = in_db_dict[entity.id].creator_id == current_user.id
            new_in_docker.append(entity)
        else:
            entity.is_in_db = False
            entity.creator = ''
            entity.action = current_user.role.name == 'super'
            new_in_docker.append(entity)
    return new_in_docker


def query_to_dict(entities_list):
    entities_dict = dict()
    for k, v in entities_list:
        entities_dict[k] = v
    return entities_dict


def get_entities_with_authority(role, entity_model, in_docker):
    # in_docker = client.volumes.list()
    group_ids = [g.id for g in current_user.groups]
    if role == 'super':
        in_db_dict = query_to_dict(entity_model.query.with_entities(entity_model.hash, entity_model).all())
        exclude_ids = []
        reverse = False
    elif role == 'group':
        in_db_dict = query_to_dict(entity_model.query.with_entities(entity_model.hash, entity_model)
                                                  .filter(or_(entity_model.access.has(Access.name == 'all'),
                                                              and_(entity_model.access.has(Access.name == 'group'),
                                                                   entity_model.groups.any(Group.id.in_(group_ids))),
                                                              entity_model.creator_id == current_user.id))
                                                  .all())
        exclude_ids = entity_model.query.with_entities(entity_model.hash).filter(
            or_(entity_model.access.has(Access.name == 'none'),
                and_(entity_model.access.has(Access.name == 'group'),
                     entity_model.groups.any(~Group.id.in_(group_ids))))).all()
        reverse = False
    else:
        in_db_dict = query_to_dict(entity_model.query.with_entities(entity_model.hash, entity_model)
                                                  .filter(or_(entity_model.access.has(Access.name == 'all'),
                                                              and_(entity_model.access.has(Access.name == 'group'),
                                                                   entity_model.groups.any(Group.id.in_(group_ids))),
                                                              entity_model.creator_id == current_user.id))
                                                  .all())
        exclude_ids = []
        reverse = True
    in_docker = merge_info(in_docker, in_db_dict, exclude_ids, reverse)
    return in_docker
