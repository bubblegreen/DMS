from app.utils.docker import docker_client
from app.models import Endpoint, Container
from flask_login import current_user
from docker.errors import DockerException, APIError
from flask import current_app
from app.utils.docker import get_entities_with_authority
from app import db


def get_containers(endpoint_id):
    role = current_user.role.name
    endpoint = Endpoint.query.get(endpoint_id)
    try:
        client = docker_client(endpoint.url)
    except (DockerException, APIError) as ex:
        current_app.logger.error(ex)
        return []
    container_in_docker = client.containers.list(all=True)
    return get_entities_with_authority(role, Container, container_in_docker)


def start_containers(endpoint_id, container_hashs):
    url = Endpoint.query.get(endpoint_id).url
    try:
        client = docker_client(url)
    except DockerException as ex:
        current_app.logger.error('Cannot connect to docker server: %s' % url)
        return False
    fail_list = []
    for container_hash in container_hashs:
        try:
            container = client.containers.get(container_hash)
            if container.status != 'running':
                container.start()
        except APIError as ex:
            current_app.logger.error('Fail to start container: %s, error: %s, user: %s',
                                     (container_hash, ex, current_user.username))
            fail_list.append(container_hash)
            continue
    if 0 < len(fail_list):
        return fail_list
    return True


def stop_containers(endpoint_id, container_hashs):
    url = Endpoint.query.get(endpoint_id).url
    try:
        client = docker_client(url)
    except DockerException as ex:
        current_app.logger.error('Cannot connect to docker server: %s' % url)
        return False
    fail_list = []
    for container_hash in container_hashs:
        try:
            container = client.containers.get(container_hash)
            if container.status != 'exited':
                container.stop()
        except APIError as ex:
            current_app.logger.error('Fail to stop container: %s, error: %s, user: %s',
                                     (container_hash, ex, current_user.username))
            fail_list.append(container_hash)
            continue
    if 0 < len(fail_list):
        return fail_list
    return True


def restart_containers(endpoint_id, container_hashs):
    url = Endpoint.query.get(endpoint_id).url
    try:
        client = docker_client(url)
    except DockerException as ex:
        current_app.logger.error('Cannot connect to docker server: %s' % url)
        return False
    fail_list = []
    for container_hash in container_hashs:
        try:
            container = client.containers.get(container_hash)
            if container.status != 'exited':
                container.restart()
        except APIError as ex:
            current_app.logger.error('Fail to restart container: %s, error: %s, user: %s',
                                     (container_hash, ex, current_user.username))
            fail_list.append(container_hash)
            continue
    if 0 < len(fail_list):
        return fail_list
    return True


def remove_containers(endpoint_id, container_hashs):
    url = Endpoint.query.get(endpoint_id).url
    try:
        client = docker_client(url)
    except DockerException as ex:
        current_app.logger.error('Cannot connect to docker server: %s' % url)
        return False
    containers_in_db = dict()
    for k, v in Container.query.with_entities(Container.hash, Container).filter(Container.hash.in_(container_hashs)).all():
        containers_in_db[k] = v
    fail_list = []
    for container_hash in container_hashs:
        try:
            container = client.containers.get(container_hash)
            container.remove()
        except APIError as ex:
            current_app.logger.error('Fail to restart container: %s, error: %s, user: %s',
                                     (container_hash, ex, current_user.username))
            fail_list.append(container_hash)
            continue
        container_in_db = containers_in_db.get(container_hash, None)
        if container_in_db:
            db.session.delete(container_in_db)
    db.session.commit()
    if 0 < len(fail_list):
        return fail_list
    return True
