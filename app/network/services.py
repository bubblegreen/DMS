from flask import current_app
from flask_login import current_user
from app.models import Endpoint, Network, Group
from app.utils.docker import docker_client, get_entities_with_authority
from app import db
from docker.errors import DockerException, APIError
from docker.types import IPAMConfig, IPAMPool


def get_networks(endpoint_id):
    role = current_user.role.name
    endpoint = Endpoint.query.get(endpoint_id)
    try:
        client = docker_client(endpoint.url)
    except (DockerException, APIError) as ex:
        current_app.logger.error(ex)
        return []
    networks_in_docker = client.networks.list()
    return get_entities_with_authority(role, Network, networks_in_docker)


def create_network(endpoint_id, form):
    endpoint = Endpoint.query.get(endpoint_id)
    groups = Group.query.filter(Group.id.in_(form.groups.data)).all()
    access_id = form.access.data
    network_db = Network()
    network_db.groups = groups
    network_db.access_id = access_id
    network_db.creator_id = current_user.id
    options = form.options.data
    labels = form.labels.data
    aux_addresses = {}
    for exclude in form.exclude_ips.data.split(';'):
        key, value = exclude.split('=')
        aux_addresses[key] = value
    ipam_pool = IPAMPool(subnet=form.subnet.data, iprange=form.ip_range.data, gateway=form.gateway.data,
                         aux_addresses=aux_addresses)
    ipam_config = IPAMConfig(pool_configs=[ipam_pool, ])
    try:
        client = docker_client(endpoint.url)
        network = client.networks.create(form.name.data, driver=form.driver.data, options=options, labels=labels,
                                         ipam=ipam_config, check_duplicate=True, internal=form.internal.data,
                                         attachable=form.attachable.data)
        network_db.hash = network.id
        db.session.add(network_db)
        db.session.commit()
        return network
    except (DockerException, APIError) as ex:
        current_app.logger.error(ex)
        return None


def get_network_by_hash(endpoint_id, network_hash):
    endpoint = Endpoint.query.get(endpoint_id)
    try:
        client = docker_client(endpoint.url)
        network = client.networks.get(network_hash)
        network.db = Network.query.filter(Network.hash == network_hash).first()
        return network
    except (DockerException, APIError) as ex:
        current_app.logger.error(ex)
        return None


def update_network(network_hash, form):
    try:
        network_in_db = Network.query.filter(Network.hash == network_hash).first()
        groups = Group.query.filter(Group.id.in_(form.groups.data)).all()
        access_id = form.access.data
        if network_in_db is not None:
            network_in_db.groups = groups
            network_in_db.access_id = access_id
        else:
            network_in_db = Network()
            network_in_db.hash = network_hash
            network_in_db.creator_id = current_user.id
            network_in_db.groups = groups
            network_in_db.access_id = access_id
            db.session.add(network_in_db)
        db.session.commit()
        return 'ok'
    except Exception as ex:
        current_app.logger.error(ex)
        return ex


def get_network_containers(endpoint_id, network_id):
    try:
        endpoint = Endpoint.query.get(endpoint_id)
        client = docker_client(endpoint.url)
        network = client.networks.get(network_id)
        return network.attrs['Containers']
    except Exception as ex:
        current_app.logger.error(ex)
        return {}


def leave_container(endpoint_id, network_id, container_id):
    try:
        endpoint = Endpoint.query.get(endpoint_id)
        client = docker_client(endpoint.url)
        network = client.networks.get(network_id)
        network.disconnect(container_id)
        return 'ok'
    except Exception as ex:
        current_app.logger.error(ex)
        return ex
