from app.network import bp
from flask import render_template, jsonify, session, request, current_app
from flask_login import login_required, current_user
from app.network import services
from app.group.services import get_all_groups
from app.network.forms import NetworkCreateForm


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
