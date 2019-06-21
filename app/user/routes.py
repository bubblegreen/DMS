from flask_login import login_required
from app.user import bp
from flask import render_template, jsonify, request, current_app
from app.models import Group, User, Permission
from app.user.forms import UpdateUserForm
from app.user import services
from app.group.services import get_all_groups_with_inactive


@bp.route('/', methods=['GET'])
@login_required
def index():
    return render_template('user/index.html')


@bp.route('/db_list', methods=['GET'])
@login_required
def get_db_list():
    users = services.get_all_users_with_inactive()
    data = {'data': []}
    for user in users:
        stat = '激活' if user.active else '禁用'
        data['data'].append(
            [user.id, user.username, user.create_date.strftime('%Y-%m-%d %H:%M:%S'),
             user.last_visit.strftime('%Y-%m-%d %H:%M:%S'), user.role.name, stat])
    return jsonify(data)


@bp.route('/update/<user_id>', methods=['GET', 'POST'])
@login_required
def update_group(user_id):
    form = UpdateUserForm()
    old_user = User.query.get(user_id)
    form.groups.choices = list((g.id, g.name) for g in get_all_groups_with_inactive())
    form.image_permission.choices = [(0, 'None'), ]
    form.container_permission.choices = [(0, 'None'), ]
    form.network_permission.choices = [(0, 'None'), ]
    form.volume_permission.choices = [(0, 'None'), ]
    form.endpoint_permission.choices = [(0, 'None'), ]
    form.image_permission.choices.extend(list(
        (p.id, p.permission_type) for p in Permission.query.filter(Permission.name == 'image')))
    form.container_permission.choices.extend(list(
        (p.id, p.permission_type) for p in Permission.query.filter(Permission.name == 'container')))
    form.network_permission.choices.extend(list(
        (p.id, p.permission_type) for p in Permission.query.filter(Permission.name == 'network')))
    form.volume_permission.choices.extend(list(
        (p.id, p.permission_type) for p in Permission.query.filter(Permission.name == 'volume')))
    form.endpoint_permission.choices.extend(list(
        (p.id, p.permission_type) for p in Permission.query.filter(Permission.name == 'endpoint')))
    if form.validate_on_submit():
        user = services.update_user(user_id, form)
        return 'ok' if user else render_template('user/edit.html', form=form, action='Update', user_id=user_id)
    form.email.data = old_user.email
    form.role.data = old_user.role_id
    form.groups.data = list(g.id for g in old_user.groups)
    image_permission = old_user.permission_info.get('image', None)
    form.image_permission.data = image_permission.id if image_permission else 0
    container_permission = old_user.permission_info.get('container', None)
    form.container_permission.data = container_permission.id if container_permission else 0
    network_permission = old_user.permission_info.get('network', None)
    form.network_permission.data = network_permission.id if network_permission else 0
    volume_permission = old_user.permission_info.get('volume', None)
    form.volume_permission.data = volume_permission.id if volume_permission else 0
    endpoint_permission = old_user.permission_info.get('endpoint', None)
    form.endpoint_permission.data = endpoint_permission.id if endpoint_permission else 0
    return render_template('user/edit.html', form=form, action='Update', user_id=user_id)


@bp.route('/remove', methods=['POST'])
@login_required
def remove_group():
    ids = request.json
    services.change_user_active(ids)
    return render_template('user/index.html')
