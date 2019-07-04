from app.models import Volume, Endpoint, Group
from flask_login import current_user
from flask import current_app
from app.utils.docker import docker_client, get_entities_with_authority
from docker.errors import DockerException, APIError
from app import db


def get_volumes(endpoint_id):
    role = current_user.role.name
    endpoint = Endpoint.query.get(endpoint_id)
    try:
        client = docker_client(endpoint.url)
    except (DockerException, APIError) as ex:
        current_app.logger.error(ex)
        return []
    volumes_in_docker = client.volumes.list()
    return get_entities_with_authority(role, Volume, volumes_in_docker)


def create_volume(endpoint_id, form):
    endpoint = Endpoint.query.get(endpoint_id)
    groups = Group.query.filter(Group.id.in_(form.groups.data)).all()
    access_id = form.access.data
    volume_db = Volume()
    volume_db.groups = groups
    volume_db.access_id = access_id
    volume_db.creator_id = current_user.id
    labels = form.labels.data
    try:
        client = docker_client(endpoint.url)
        volume = client.volumes.create(form.name.data, driver=form.driver.data, labels=labels)
        volume_db.hash = volume.id
        db.session.add(volume_db)
        db.session.commit()
        return volume
    except (DockerException, APIError) as ex:
        current_app.logger.error(ex)
        return None


def update_volume(form):
    try:
        groups = Group.query.filter(Group.id.in_(form.groups.data)).all()
        access_id = form.access.data
        volume_in_db = Volume.query.filter(Volume.hash == form.name.data).first()
        if volume_in_db is None:
            volume_in_db = Volume()
            volume_in_db.hash = form.name.data
            volume_in_db.creator_id = current_user.id
            db.session.add(volume_in_db)
        volume_in_db.groups = groups
        volume_in_db.access_id = access_id
        db.session.commit()
        return 'ok'
    except Exception as ex:
        form.name.errors.append(ex)
        return ex


def get_volume_by_hash(endpoint_id, volume_hash):
    endpoint = Endpoint.query.get(endpoint_id)
    try:
        client = docker_client(endpoint.url)
        volume = client.volumes.get(volume_hash)
        volume.db = Volume.query.filter(Volume.hash == volume_hash).first()
        return volume
    except (DockerException, APIError) as ex:
        current_app.logger.error(ex)
        return None


def remove_volumes(endpoint_id, hashs):
    url = Endpoint.query.get(endpoint_id).url
    try:
        client = docker_client(url)
    except DockerException as ex:
        current_app.logger.error('Cannot connect to docker server: %s' % url)
        return False
    volumes_in_db = dict()
    for k, v in Volume.query.with_entities(Volume.hash, Volume).filter(Volume.hash.in_(hashs)).all():
        volumes_in_db[k] = v
    fail_list = []
    for hash in hashs:
        try:
            volume = client.volumes.get(hash)
            volume.remove()
        except APIError as ex:
            current_app.logger.error('Fail to remove image: %s, error: %s, user: %s',
                                     (hash, ex, current_user.username))
            fail_list.append(hash)
            continue
        image_in_db = volumes_in_db.get(hash, None)
        if image_in_db:
            db.session.delete(image_in_db)
    db.session.commit()
    if 0 < len(fail_list):
        return fail_list
    return True
