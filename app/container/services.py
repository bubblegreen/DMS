from app.utils.docker import docker_client
from app.models import Endpoint, Container
from flask_login import current_user
from docker.errors import DockerException, APIError
from flask import current_app
from app.utils.docker import get_entities_with_authority


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
