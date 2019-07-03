from flask_login import login_required
from app.group import bp
from flask import render_template, jsonify, request, current_app
from app.models import Group, User
from app.group.forms import AddGroupForm, UpdateGroupForm
from app.group import services


@bp.route('/', methods=['GET'])
@login_required
def index():
    return render_template('group/index.html')


@bp.route('/db_list', methods=['GET'])
@login_required
def get_db_list():
    groups = services.get_all_groups()
    data = {'data': []}
    for group in groups:
        data['data'].append(
            [group.id, group.name, group.create_time.strftime('%Y-%m-%d %H:%M:%S'), group.creator.username])
    return jsonify(data)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def add_group():
    form = AddGroupForm()
    form.members.choices = list((u.id, u.username) for u in User.query.filter(User.active).all())
    if form.validate_on_submit():
        group = services.add_group(form)
        current_app.logger.info(form.members.choices)
        return 'ok' if group else render_template('group/edit.html', form=form, action='New')
    return render_template('group/edit.html', form=form, action='New')


@bp.route('/update/<group_id>', methods=['GET', 'POST'])
@login_required
def update_group(group_id):
    form = UpdateGroupForm()
    form.members.choices = list((u.id, u.username) for u in User.query.all())
    old_group = Group.query.get(group_id)
    if form.validate_on_submit():
        if old_group.name != form.name.data:
            e = Group.query.filter(Group.name == form.name.data).first()
            if e is not None:
                form.name.errors.append('名称已存在，请重新输入！')
                return render_template('group/edit.html', form=form, action='Update', group_id=group_id)
        group = services.update_group(group_id, form)
        return 'ok' if group else render_template('group/edit.html', form=form, action='Update', group_id=group_id)
    form.name.data = old_group.name
    form.desc.data = old_group.desc
    form.members.data = list(u.id for u in old_group.members)
    return render_template('group/edit.html', form=form, action='Update', group_id=group_id)


@bp.route('/remove', methods=['POST'])
@login_required
def remove_group():
    ids = request.json
    result = services.remove_group(ids)
    return jsonify(result)
