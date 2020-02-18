from app.models import Endpoint, Group, Permission, Access
from docker.errors import DockerException, APIError
from flask import current_app
from app.utils.docker import docker_client
from app import db
from flask_login import current_user
from multiprocessing.pool import Pool


def check_endpoint_available(endpoint):
    url = endpoint.url
    try:
        docker_client(url)
        return True
    except DockerException as ex:
        current_app.logger.error('Cannot connect to endpoint:%s' % url)
        return False


def get_all_endpoint_infos():
    endpoints = []
    endpoint_list = get_all_endpoint_from_db()
    # for endpoint in endpoint_list:
    #     endpoint_info_dict = get_endpoint_info(endpoint)
    #     endpoint_info_dict['db'] = endpoint
    #     endpoints.append(endpoint_info_dict)
    results = []
    with Pool(processes=4) as pool:
        for endpoint in endpoint_list:
            result = pool.apply_async(get_endpoint_info, (endpoint, ))
            results.append(result)
        pool.close()
        pool.join()
    for result in results:
        endpoints.append(result.get())
    return endpoints


def get_endpoint_info(endpoint):
    endpoint_info_dict = dict()
    endpoint_info_dict['db'] = endpoint
    try:
        client = docker_client(endpoint.url)
        info = client.info()
        endpoint_info_dict['stat'] = 'up'
        endpoint_info_dict['containers_num'] = info['Containers']
        endpoint_info_dict['container_run_num'] = info['ContainersRunning']
        endpoint_info_dict['container_stop_num'] = info['ContainersStopped']
        endpoint_info_dict['images_num'] = info['Images']
        endpoint_info_dict['mode'] = get_endpoint_mode(endpoint.id)
        endpoint_info_dict['version'] = info['ServerVersion']
        endpoint_info_dict['cpu_num'] = info['NCPU']
        endpoint_info_dict['mem_num'] = int(info['MemTotal'] / 1000 / 1000 / 1000)
        # todo stacks
        endpoint_info_dict['stacks_num'] = 0
        endpoint_info_dict['services_num'] = len(client.services.list()) if info['Swarm']['ControlAvailable'] else 0
        endpoint_info_dict['volumes_num'] = len(client.volumes.list())
        endpoint_info_dict['networks_num'] = len(client.networks.list())
    except APIError as ex:
        endpoint_info_dict['stat'] = 'error'
    except DockerException as ex:
        endpoint_info_dict['stat'] = 'down'
    return endpoint_info_dict


def get_endpoint_mode(endpoint_id):
    endpoint = Endpoint.query.get(endpoint_id)
    try:
        client = docker_client(endpoint.url)
        info = client.info()
        mode = 'Standalone' if not info['Swarm']['NodeID'] else (
            'Node' if not info['Swarm']['ControlAvailable'] else 'Swarm')
        return mode
    except (DockerException, APIError) as ex:
        return ''


def get_all_endpoint_from_db():
    role = current_user.role.name
    if role == 'super':
        endpoints = Endpoint.query.all()
    else:
        if current_user.permission_info.get('endpoint', None) is not None:
            endpoints = Endpoint.query.filter(Endpoint.access.has(Access.name == 'all')).all()
            group_ids = [g.id for g in current_user.groups]
            endpoints.extend(Endpoint.query.filter(Endpoint.access.has(Access.name == 'group')).filter(
                Endpoint.groups.any(Group.id.in_(group_ids))).all())
        else:
            endpoints = []
    return endpoints


def add_endpoint(form):
    try:
        endpoint = Endpoint()
        endpoint.name = form.name.data
        endpoint.url = form.url.data
        endpoint.groups = Group.query.filter(Group.id.in_(form.groups.data)).all()
        endpoint.access_id = form.access.data
        endpoint.creator_id = current_user.id
        db.session.add(endpoint)
        db.session.commit()
        return endpoint
    except Exception as ex:
        current_app.logger.error(ex)
        return None


def update_endpoint(endpoint_id, form):
    try:
        endpoint = Endpoint.query.get(endpoint_id)
        endpoint.name = form.name.data
        endpoint.url = form.url.data
        endpoint.groups = Group.query.filter(Group.id.in_(form.groups.data)).all()
        endpoint.access_id = form.access.data
        db.session.commit()
        return endpoint
    except Exception as ex:
        current_app.logger.error(ex)
        return None


def remove_endpoint(ids):
    try:
        endpoints = Endpoint.query.filter(Endpoint.id.in_(ids))
        for endpoint in endpoints:
            db.session.delete(endpoint)
        db.session.commit()
        return []
    except Exception as ex:
        current_app.logger.error(ex)
        return ids

#
# def __docker_client(url):
#     return docker.DockerClient(base_url=url, version='auto', timeout=5)
