from flask_login import login_required, current_user
from app.endpoint import bp
from flask import render_template, jsonify, request, current_app
from app.models import Endpoint, Group
from app.endpoint.forms import AddEndpointForm, UpdateEndpointForm
from app.endpoint import services


@bp.route('/', methods=['GET'])
@login_required
def index():
    return render_template('endpoint/index.html')


@bp.route('/db_list', methods=['GET'])
@login_required
def get_db_list():
    endpoints = services.get_all_endpoint_from_db()
    data = {'data': []}
    for endpoint in endpoints:
        data['data'].append([endpoint.id, endpoint.name, endpoint.url])
    return jsonify(data)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def add_endpoint():
    form = AddEndpointForm()
    form.groups.choices = list((g.id, g.name) for g in Group.query.filter(Group.active).all())
    if form.validate_on_submit():
        endpoint = services.add_endpoint(form)
        return 'ok' if endpoint else render_template('endpoint/edit.html', form=form, action='New', endpoint_id='')
    return render_template('endpoint/edit.html', form=form, action='New', endpoint_id='')


@bp.route('/update/<endpoint_id>', methods=['GET', 'POST'])
@login_required
def update_endpoint(endpoint_id):
    form = UpdateEndpointForm()
    form.groups.choices = list((g.id, g.name) for g in Group.query.all())
    old_endpoint = Endpoint.query.get(endpoint_id)
    if form.validate_on_submit():
        if old_endpoint.name != form.name.data:
            e = Endpoint.query.filter(Endpoint.name == form.name.data).first()
            if e is not None:
                form.name.errors.append('名称已存在，请重新输入！')
                return render_template('endpoint/edit.html', form=form, action='Update', endpoint_id=endpoint_id)
        if old_endpoint.url != form.url.data:
            e = Endpoint.query.filter(Endpoint.url == form.url.data).first()
            if e is not None:
                form.url.errors.append('名称已存在，请重新输入！')
                return render_template('endpoint/edit.html', form=form, action='Update', endpoint_id=endpoint_id)
        endpoint = services.update_endpoint(endpoint_id, form)
        return 'ok' if endpoint else render_template('endpoint/edit.html', form=form, action='Update',
                                                     endpoint_id=endpoint_id)
    current_app.logger.info(form.groups.errors)
    form.name.data = old_endpoint.name
    form.url.data = old_endpoint.url
    form.access.data = old_endpoint.access_id
    form.groups.data = list(g.id for g in old_endpoint.groups)
    return render_template('endpoint/edit.html', form=form, action='Update', endpoint_id=endpoint_id)


@bp.route('/remove', methods=['POST'])
@login_required
def remove_endpoint():
    ids = request.json
    services.remove_endpoint(ids)
    return render_template('endpoint/index.html')
