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
