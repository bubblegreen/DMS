from datetime import datetime
from app import db
from flask_login import current_user, login_required
from app.main import bp
from flask import render_template, current_app, session, jsonify, send_file, url_for
from app.models import Endpoint
from app.endpoint import services


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_visit = datetime.now()
        db.session.commit()


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    role = current_user.role.name
    endpoint_id = session.get('endpoint_id', '')
    endpoint = Endpoint.query.get(endpoint_id)
    mode = services.get_endpoint_mode(endpoint.id) if endpoint else ''
    name = endpoint.name if endpoint else ''
    endpoint_list = services.get_all_endpoint_infos()
    permissions = dict()
    for k, v in current_user.permission_info.items():
        permissions[k] = v.permission_type
    return render_template('index.html', title='首页', role=role, mode=mode, endpoint_name=name,
                           endpoint_list=endpoint_list, permissions=permissions)


@bp.route('/dashboard')
@login_required
def dashboard():
    endpoint_id = session.get('endpoint_id', '')
    endpoint = Endpoint.query.get(endpoint_id)
    endpoint_info = services.get_endpoint_info(endpoint)
    endpoint_info['db'] = endpoint
    menu_list = ['stacks_num', 'services_num', 'containers_num', 'images_num', 'volumes_num', 'networks_num']
    if endpoint_info.get('mode', '').lower() != 'swarm':
        menu_list.remove('services_num')
    return render_template('dashboard.html', endpoint=endpoint_info,
                           menu_list=menu_list)


@bp.route('/load/<endpoint_id>')
@login_required
def load_endpoint(endpoint_id):
    session['endpoint_id'] = endpoint_id
    endpoint = Endpoint.query.get(endpoint_id)
    mode = services.get_endpoint_mode(endpoint_id)
    role = current_user.role.name
    return jsonify(name=endpoint.name, mode=mode, role=role)
