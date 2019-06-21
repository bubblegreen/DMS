from flask_login import login_required, current_user
from app.image import bp
from flask import render_template, jsonify, request, current_app, session
from app.image import services
from app.image.forms import ImagePullForm
from app.registry.services import get_registries


@bp.route('/')
@login_required
def index():
    permission = current_user.permission_info.get('image', None)
    permission = permission.permission_type if permission else ''
    form = ImagePullForm()
    form.registry.choices = list((r.id, r.name) for r in get_registries())
    pull_form_content = render_template('image/pull_form_content.html', form=form)
    return render_template('image/index.html', permission=permission, pull_form_content=pull_form_content)


@bp.route('/db_list')
@login_required
def get_images():
    endpoint_id = session.get('endpoint_id', '')
    images = {'data': []}
    for image in services.get_images(endpoint_id):
        size = '%.1f' % (image.attrs['Size'] / 1000 / 1000)
        if len(size[:size.index('.')]) <= 3:
            size = size.replace('.0', '') + 'MB'
        else:
            size = '%.1f' % (image.attrs['Size'] / 1000 / 1000 / 1000)
            size = size.replace('.0', '') + 'GB'
        create = image.attrs['Created']
        create = create[:create.index('.')].replace('T', ' ')
        images['data'].append([image.attrs['Id'], image.attrs['RepoTags'], size, create, image.action])
    return jsonify(images)


@bp.route('/pull', methods=['POST'])
@login_required
def pull_image():
    endpoint_id = session.get('endpoint_id', '')
    form = ImagePullForm()
    form.registry.choices = list((r.id, r.name) for r in get_registries())
    if form.validate_on_submit():
        image = services.pull_image(endpoint_id, form)
        if image:
            msg = 'Pull image: %s success!'
        else:
            msg = 'Pull image fail, please contact admin'
        return jsonify({'msg': msg})
    else:
        html = render_template('image/pull_form_content.html', form=form)
        return jsonify({'html': html})


@bp.route('/remove', methods=['POST'])
@login_required
def remove_images():
    image_hashs = request.json
    endpoint_id = session.get('endpoint_id', '')
    result = services.remove_images(endpoint_id, image_hashs)
    if isinstance(result, list):
        return jsonify(result)
    else:
        return jsonify([])


@bp.route('/new', methods= ['GET', 'POST'])
@login_required
def create_image():
    # todo
    pass
