from app.registry import bp
from flask import render_template, jsonify, session, request, current_app
from flask_login import login_required, current_user
from app.registry import services
from app.registry.forms import AddRegistryForm, UpdateRegistryForm
from app.models import Group, Registry


@bp.route('/')
@login_required
def index():
    return render_template('registry/index.html')


@bp.route('/db_list')
@login_required
def get_registry_list():
    registries = services.get_registries()
    data = {'data': []}
    for registry in registries:
        data['data'].append([registry.id, registry.name, registry.url])
    return jsonify(data)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def add_registry():
    form = AddRegistryForm()
    form.groups.choices = list((g.id, g.name) for g in Group.query.filter(Group.active).all())
    if form.validate_on_submit():
        registry = services.add_registry(form)
        return 'ok' if registry else render_template('registry/edit.html', form=form, action='New', registry_id='')
    return render_template('registry/edit.html', form=form, action='New', registry_id='')


@bp.route('/update/<registry_id>', methods=['GET', 'POST'])
@login_required
def update_endpoint(registry_id):
    form = UpdateRegistryForm()
    form.groups.choices = list((g.id, g.name) for g in Group.query.all())
    old_registry = Registry.query.get(registry_id)
    if form.validate_on_submit():
        if old_registry.name != form.name.data:
            e = Registry.query.filter(Registry.name == form.name.data).first()
            if e is not None:
                form.name.errors.append('名称已存在，请重新输入！')
                return render_template('registry/edit.html', form=form, action='Update', registry_id=registry_id)
        if old_registry.url != form.url.data:
            r = Registry.query.filter(Registry.url == form.url.data).first()
            if r is not None:
                form.url.errors.append('名称已存在，请重新输入！')
                return render_template('registry/edit.html', form=form, action='Update', registry_id=registry_id)
        registry = services.update_registry(registry_id, form)
        return 'ok' if registry else render_template('registry/edit.html', form=form, action='Update',
                                                     registry_id=registry_id)
    current_app.logger.info(form.groups.errors)
    form.name.data = old_registry.name
    form.url.data = old_registry.url
    form.access.data = old_registry.access_id
    form.groups.data = list(g.id for g in old_registry.groups)
    return render_template('registry/edit.html', form=form, action='Update', registry_id=registry_id)


@bp.route('/remove', methods=['POST'])
@login_required
def remove_registry():
    ids = request.json
    result = services.remove_registry(ids)
    return jsonify(result)
