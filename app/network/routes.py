from app.network import bp
from flask import render_template, jsonify, session, request, current_app
from flask_login import login_required, current_user
from app.network import services
from app.group.services import get_all_groups
from app.network.forms import NetworkCreateForm, NetworkManageForm


@bp.route('/')
@login_required
def index():
    permission = current_user.permission_info.get('network', None)
    permission = permission.permission_type if permission else ''
    return render_template('network/index.html', permission=permission)


@bp.route('/db_list')
@login_required
def get_networks():
    endpoint_id = session.get('endpoint_id', '')
    networks = {'data': []}
    for network in services.get_networks(endpoint_id):
        create = network.attrs['Created']
        create = create[:create.index('.')].replace('T', ' ')
        if network.attrs['Labels'] and (
                'com.docker.compose.project' in network.attrs['Labels'].keys()
                or 'com.docker.stack.namespace' in network.attrs['Labels'].keys()):
            stack = network.attrs['Labels'].get('com.docker.compose.project', None) or network.attrs['Labels'].get(
                'com.docker.stack.namespace', None)
        else:
            stack = '-'
        if len(network.attrs['IPAM']['Config']) > 0:
            subnet = network.attrs['IPAM']['Config'][0]['Subnet']
            gateway = network.attrs['IPAM']['Config'][0]['Gateway']
        else:
            subnet = ''
            gateway = ''
        networks['data'].append([network.id, network.name, stack, network.attrs['Scope'], network.attrs['Driver'],
                                 network.attrs['Attachable'], network.attrs['Internal'],
                                 network.attrs['IPAM']['Driver'], subnet, gateway, create, network.action])
    return jsonify(networks)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def create_network():
    endpoint_id = session.get('endpoint_id', '')
    form = NetworkCreateForm()
    form.groups.choices = list((g.id, g.name) for g in get_all_groups())
    if form.validate_on_submit():
        network = services.create_network(endpoint_id, form)
        if network:
            return 'ok'
        else:
            return render_template('network/edit.html', form=form, action='New')
    return render_template('network/edit.html', form=form, action='New')


@bp.route('/update/<network_hash>', methods=['GET', 'POST'])
@login_required
def update_network(network_hash):
    endpoint_id = session.get('endpoint_id', '')
    form = NetworkManageForm()
    form.groups.choices = list((g.id, g.name) for g in get_all_groups())
    if form.validate_on_submit():
        network = services.update_network(network_hash, form)
        return network
    network = services.get_network_by_hash(endpoint_id, network_hash)
    containers = []
    subnet = ''
    gateway = ''
    if network:
        ipam_config = network.attrs['IPAM']['Config']
        subnet = ipam_config[0]['Subnet'] if len(ipam_config) > 0 else ''
        gateway = ipam_config[0]['Gateway'] if len(ipam_config) > 0 else ''
        containers = network.attrs['Containers']
    if network.db is not None:
        form.groups.data = [g.id for g in network.db.groups]
        form.access.data = network.db.access_id
    return render_template('network/detail.html', form=form, network=network, containers=containers, action='Update',
                           subnet=subnet, gateway=gateway)


@bp.route('/containers/<network_hash>')
@login_required
def get_network_containers(network_hash):
    endpoint_id = session.get('endpoint_id', '')
    containers = services.get_network_containers(endpoint_id, network_hash)
    html = render_template('network/container-list.html', containers=containers)
    return html


@bp.route('/container/leave', methods=['POST'])
@login_required
def leave_container():
    endpoint_id = session.get('endpoint_id', '')
    params = request.json
    network_id = params['network_id']
    container_id = params['container_id']
    result = services.leave_container(endpoint_id, network_id, container_id)
    return result
