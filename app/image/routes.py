from flask_login import login_required, current_user
from app.image import bp
from flask import render_template, jsonify, request, current_app, session
from app.image import services
from app.image.forms import ImagePullForm, ImageBuildForm, ImageManageForm
from app.registry.services import get_registries
from app.group.services import get_all_groups


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


@bp.route('/detail/<image_hash>', methods=['GET'])
@login_required
def get_image_detail(image_hash):
    endpoint_id = session.get('endpoint_id', '')
    image = services.get_image_by_id(endpoint_id, image_hash)
    tag_list = render_template('image/tag_list.html', image=image)
    form = ImagePullForm()
    form.registry.choices = list((r.id, r.name) for r in get_registries())
    tag = render_template('image/tag.html', form=form)
    mng_form = ImageManageForm()
    mng_form.groups.choices = list((g.id, g.name) for g in get_all_groups())
    if image.db:
        mng_form.groups.data = list(g.id for g in image.db.groups)
        mng_form.access.data = image.db.access_id
    return render_template('image/detail.html', image=image, tag_list=tag_list, tag=tag, form=mng_form)


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


@bp.route('/build', methods=['GET', 'POST'])
@login_required
def create_image():
    endpoint_id = session.get('endpoint_id')
    form = ImageBuildForm()
    form.groups.choices = list((g.id, g.name) for g in get_all_groups())
    tags = []
    for image in services.get_images(endpoint_id):
        tags.extend(image.tags)
    form.base_image.choices = list((t, t) for t in tags)
    if form.validate_on_submit():
        rs = services.build_image(endpoint_id, form)
        if isinstance(rs, ImageBuildForm):
            return render_template('image/build.html', form=form, action='Build')
        return 'ok'
    current_app.logger.info(form.errors)
    return render_template('image/build.html', form=form, action='Build')


@bp.route('/tag/<image_hash>', methods=['POST'])
@login_required
def tag_image(image_hash):
    endpoint_id = session.get('endpoint_id')
    form = ImagePullForm()
    form.registry.choices = list((r.id, r.name) for r in get_registries())
    if form.validate_on_submit():
        image = services.tag_image(endpoint_id, image_hash, form)
        if not isinstance(image, str):
            current_app.logger.info('return ok')
            return jsonify('ok')
        else:
            return image
    current_app.logger.info(form.errors)
    return form.errors


@bp.route('/tag_list/<image_hash>')
@login_required
def get_image_tag_list(image_hash):
    endpoint_id = session.get('endpoint_id')
    image = services.get_image_by_id(endpoint_id, image_hash)
    return render_template('image/tag_list.html', image=image)


@bp.route('/untag', methods=['POST'])
@login_required
def untag_image():
    tag = request.json.get('tag')
    current_app.logger.info('enter untag:%s' % tag)
    endpoint_id = session.get('endpoint_id')
    result = services.untag_image(endpoint_id, tag)
    if result:
        return 'ok'
    else:
        return 'fail'


@bp.route('/update/<image_hash>', methods=['POST'])
@login_required
def update_image(image_hash):
    form = ImageManageForm()
    form.groups.choices = list((g.id, g.name) for g in get_all_groups())
    if form.validate_on_submit():
        return services.update_image(image_hash, form)
    return form.errors[0]
