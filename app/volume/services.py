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
    labels = {}
    # todo need debug label
    for k, v in zip(form.label_name.data, form.label_value.data):
        labels[k] = v
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
