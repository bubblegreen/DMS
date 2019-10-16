from app.container import bp
from flask_login import login_required, current_user
from flask import request, session, render_template, jsonify, current_app
from app.container import services
from app.container.forms import ContainerCreateForm, ContainerUpdateForm
from app.group.services import get_all_groups
from app.image.services import get_images_tag_list
from app.volume.services import get_volumes
from app.network.services import get_networks, join_container, get_network_by_name


@bp.route('/')
@login_required
def index():
    permission = current_user.permission_info.get('container', None)
    permission = permission.permission_type if permission else ''
    return render_template('container/index.html', permission=permission)


@bp.route('/db_list')
@login_required
def get_containers():
    endpoint_id = session.get('endpoint_id', '')
    containers = {'data': []}
    for container in services.get_containers(endpoint_id):
        create = container.attrs['Created']
        create = create[:create.index('.')].replace('T', ' ')
        if 'com.docker.compose.project' in container.labels:
            stack = container.labels['com.docker.compose.project']
        else:
            stack = ''
        image_name = container.attrs['Config']['Image']
        if image_name.startswith('sha256:'):
            image_name = image_name[7:19]
        ip = container.attrs['NetworkSettings']['IPAddress']
        port = []
        for k, v in container.ports.items():
            if v is not None:
                port.append('%s:%s' % (v[0]['HostPort'], k))
        containers['data'].append(
            [container.id, container.name, container.status, stack, image_name, ip, port, create, container.action,
             container.attrs['Image']])
    return jsonify(containers)


@bp.route('/action/<action>', methods=['POST'])
@login_required
def container_action(action):
    endpoint_id = session.get('endpoint_id', '')
    container_hashs = request.json
    func_name = action + '_containers'
    func = getattr(services, func_name)
    result = func(endpoint_id, container_hashs)
    if isinstance(result, list):
        return jsonify(result)
    else:
        return jsonify([])


@bp.route('/new', methods=['POST', 'GET'])
@login_required
def create_container():
    endpoint_id = session.get('endpoint_id')
    form = ContainerCreateForm()
    form.groups.choices = list((g.id, g.name) for g in get_all_groups())
    form.image.choices = get_images_tag_list(endpoint_id)
    volume_choices = list((v.id, v.name) for v in get_volumes(endpoint_id))
    volume_choices.insert(0, ('', ''))
    form.volume.set_volumes(volume_choices)
    form.volume_name.choices = volume_choices
    form.network.choices = list((n.id, n.name) for n in get_networks(endpoint_id))
    default = get_network_by_name(endpoint_id)
    form.network.default = default.id
    form.process()
    if form.validate_on_submit():
        result = services.run_container(endpoint_id, form)
        if result != 'ok':
            form.name.errors = [result, ]
            return render_template('container/create.html', form=form, action='Create')
        else:
            return result
    current_app.logger.info(form.errors)
    return render_template('container/create.html', form=form, action='Create')


@bp.route('/update/<container_hash>', methods=['GET', 'POST'])
@login_required
def update_container(container_hash):
    endpoint_id = session.get('endpoint_id')
    form = ContainerUpdateForm()
    form.groups.choices = list((g.id, g.name) for g in get_all_groups())
    form.networks.choices = list((n.id, n.name) for n in get_networks(endpoint_id))
    container = services.get_container(endpoint_id, container_hash)
    if container.db is not None:
        form.access.data = container.db.access_id
        form.groups.data = [g.id for g in container.db.groups]
    networks = container.attrs['NetworkSettings']['Networks']
    network_list = render_template('container/network-list.html', networks=networks)
    return render_template('container/detail.html', container=container, form=form, network_list=network_list)


@bp.route('/rename/<container_hash>', methods=['POST'])
@login_required
def rename_container(container_hash):
    endpoint_id = session.get('endpoint_id')
    new_name = request.json['name']
    result = services.rename_container(endpoint_id, container_hash, new_name)
    return jsonify({'result': result})


@bp.route('/permission/<container_hash>', methods=['POST'])
@login_required
def update_permission(container_hash):
    form = ContainerUpdateForm()
    form.groups.choices = list((g.id, g.name) for g in get_all_groups())
    if form.is_submitted():
        result = services.update_permission(container_hash, form)
    else:
        result = form.errors
    return jsonify({'result': result})


@bp.route('/join/<container_hash>', methods=['POST'])
@login_required
def join_network(container_hash):
    endpoint_id = session.get('endpoint_id')
    network_id = request.json['network_id']
    result = join_container(endpoint_id, network_id, container_hash)
    return jsonify({'result': result})


@bp.route('/networks/<container_hash>', methods=['GET'])
@login_required
def get_network_list(container_hash):
    endpoint_id = session.get('endpoint_id')
    container = services.get_container(endpoint_id, container_hash)
    networks = container.attrs['NetworkSettings']['Networks']
    network_list = render_template('container/network-list.html', networks=networks)
    return network_list


@bp.route('/leave/<container_hash>', methods=['POST'])
@login_required
def leave_network(container_hash):
    endpoint_id = session.get('endpoint_id')
    network_name = request.json['network_name']

