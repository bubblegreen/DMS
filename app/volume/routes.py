from app.volume import bp
from flask_login import login_required, current_user
from flask import render_template, session, jsonify, current_app, request
from app.volume import services
from app.volume.forms import VolumeCreateForm
from app.group.services import get_all_groups


@bp.route('/')
@login_required
def index():
    permission = current_user.permission_info.get('volume', None)
    permission = permission.permission_type if permission else ''
    return render_template('volume/index.html', permission=permission)


@bp.route('/db_list')
@login_required
def get_volumes():
    endpoint_id = session.get('endpoint_id', '')
    volumes = {'data': []}
    for volume in services.get_volumes(endpoint_id):
        if len(volume.id) > 40:
            entity_id = volume.id[:37] + '...'
        else:
            entity_id = volume.id
        if len(volume.attrs['Mountpoint']) > 40:
            mount_point_pre = volume.attrs['Mountpoint'][:volume.attrs['Mountpoint'].rindex('/') - len(volume.id)]
            mount_point_post = volume.attrs['Mountpoint'][volume.attrs['Mountpoint'].rindex('/'):]
            mount_point = '%s...%s' % (mount_point_pre, mount_point_post)
        else:
            mount_point = volume.attrs['Mountpoint']
        create = volume.attrs['CreatedAt']
        create = create[:create.index('+')].replace('T', ' ')
        volumes['data'].append([entity_id, volume.attrs['Driver'], mount_point, create, volume.action, volume.id])
    return jsonify(volumes)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def create_volume():
    endpoint_id = session.get('endpoint_id', '')
    form = VolumeCreateForm()
    form.groups.choices = list((g.id, g.name) for g in get_all_groups())
    if form.validate_on_submit():
        volume = services.create_volume(endpoint_id, form)
        if volume:
            return 'ok'
        else:
            return render_template('volume/edit.html', form=form, action='New')
    return render_template('volume/edit.html', form=form, action='New')


@bp.route('/update/<volume_hash>', methods=['GET', 'POST'])
@login_required
def update_volume(volume_hash):
    endpoint_id = session.get('endpoint_id', '')
    form = VolumeCreateForm()
    form.groups.choices = list((g.id, g.name) for g in get_all_groups())
    if form.is_submitted():
        volume = services.update_volume(form)
        return volume
    volume = services.get_volume_by_hash(endpoint_id, volume_hash)
    if volume:
        form.name.data = volume.id
        form.groups.data = [g.id for g in volume.db.groups] if volume.db else []
        form.access.data = volume.db.access_id if volume.db else 1
        form.driver.data = volume.attrs['Driver']
        form.labels.data = volume.attrs['Labels']
    return render_template('volume/edit.html', form=form, action='Update')


@bp.route('/remove', methods=['POST'])
@login_required
def remove_volume():
    volume_hashs = request.json
    endpoint_id = session.get('endpoint_id', '')
    result = services.remove_volumes(endpoint_id, volume_hashs)
    if isinstance(result, list):
        return jsonify(result)
    else:
        return jsonify([])
