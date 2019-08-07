from app.container import bp
from flask_login import login_required, current_user
from flask import request, session, render_template, jsonify
from app.container import services
from app.container.forms import ContainerCreateForm
from app.group.services import get_all_groups
from app.image.services import get_images_tag_list
from app.volume.services import get_volumes
from app.network.services import get_networks


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
    form.volume.set_volumes(volume_choices)
    form.volume_name.choices = volume_choices
    form.network.choices = list((n.id, n.name) for n in get_networks(endpoint_id))
    if form.validate_on_submit():
        pass
    return render_template('container/create.html', form=form, action='Create')
