from app.utils.docker import docker_client
from app.models import Endpoint, Container, Group
from flask_login import current_user
from docker.errors import DockerException, APIError, ContainerError, ImageNotFound
from sqlalchemy.exc import DBAPIError
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


def run_container(endpoint_id, form):
    url = Endpoint.query.get(endpoint_id).url
    container_obj = None
    try:
        client = docker_client(url)
    except DockerException:
        current_app.logger.error('Cannot connect to docker server: %s' % url)
        return False
    access_id = form.access.data
    group_ids = form.groups.data
    image_hash = form.image.data
    command = form.command.data
    if command == '':
        command = None
    kw = {
        'detach': True,
        'name': form.name.data,
        'auto_remove': form.auto_remove.data,
        'publish_all_ports': form.publish_all_port.data,
        'ports': {},
        'volumes': {},
        'network': form.network.data,
        'environment': {},
        'labels': {},
        'privileged': form.privileged.data,
        'devices': []
    }
    for host, container in form.publish_port.data.items():
        if ':' in host:
            host = host.split(':')
            host[1] = int(host[1])
        elif host == '':
            host = None
        else:
            host = int(host)
        if '/tcp' not in container.lower() or '/udp' not in container.lower():
            container = container + '/tcp'
        kw['ports'][container] = host
    if form.restart.data != 'never':
        kw['restart_policy'] = {'Name': form.restart.data, 'MaximumRetryCount': 5}
    if form.entrypoint.data != '':
        kw['entrypoint'] = form.entrypoint.data
    if form.workdir.data != '':
        kw['working_dir'] = form.workdir.data
    if form.user.data != '':
        kw['user'] = form.user.data
    for container, host in form.volume.data.items():
        container = {'bind': container}
        kw['volumes'][host] = {'bind': container, 'mode': 'rw'}
    if form.hostname.data != '':
        kw['hostname'] = form.hostname.data
    if form.domain.data != '':
        kw['domainname'] = form.domain.data
    if form.mac.data != '':
        kw['mac_address'] = form.mac.data
    if len(form.env.data) > 0:
        kw['environment'] = form.env.data
    if len(form.labels.data) > 0:
        kw['labels'] = form.labels.data
    for host, container in form.devices.data:
        device = '%s:%s:rwm' % (host, container)
        kw['devices'].append(device)
    if form.mem_soft_limit.data != '':
        kw['mem_reservation'] = form.mem_soft_limit.data
    if form.mem_limit.data != '':
        kw['mem_limit'] = form.mem_limit.data
    if form.cpu.data != '':
        kw['cpuset_cpus'] = form.cpu.data
    try:
        container_obj = client.containers.run(image_hash, command, **kw)
        container_in_db = Container()
        container_in_db.hash = container_obj.id
        container_in_db.creator_id = current_user.id
        container_in_db.access_id = access_id
        container_in_db.groups = Group.query.filter(Group.id.in_(group_ids)).all()
        db.session.add(container_in_db)
        db.session.commit()
        return 'ok'
    except (APIError, ContainerError, ImageNotFound) as ex:
        return ex
    except DBAPIError as ex:
        if container_obj is not None:
            container_obj.remove(force=True)
        return ex
