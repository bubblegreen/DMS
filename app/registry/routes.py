from app.registry import bp
from flask import render_template, jsonify, session, request, current_app
from flask_login import login_required, current_user
from app.registry import services


@bp.route('/')
@login_required
def index():
    return render_template('registry/index.html')


@bp.route('/list')
@login_required
def get_registry_list():
    registries = services.get_registries()
    data = {'data': []}
    for registry in registries:
        data['data'].append([registry.id, registry.name, registry.url])
    return jsonify(data)
