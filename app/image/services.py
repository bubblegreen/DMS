from docker.errors import DockerException, APIError
from app.models import Image, Group, Endpoint, Access, User, Role, Registry
from flask_login import current_user
from app.utils.docker import docker_client
from sqlalchemy import or_, and_
from app import db
from flask import current_app


def get_images(endpoint_id):
    role = current_user.role.name
    endpoint = Endpoint.query.get(endpoint_id)
    try:
        client = docker_client(endpoint.url)
    except (DockerException, APIError) as ex:
        return []
    images_in_docker = client.images.list()
    group_ids = [g.id for g in current_user.groups]
    if role == 'super':
        images_in_db_dict = image_query_to_dict(Image.query.with_entities(Image.image_hash, Image).all())
        images_exclude_ids = []
        reverse = False
    elif role == 'group':
        images_in_db_dict = image_query_to_dict(Image.query.with_entities(Image.image_hash, Image)
                                                .filter(or_(Image.access.has(Access.name == 'all'),
                                                            and_(Image.access.has(Access.name == 'group'),
                                                                 Image.groups.any(Group.id.in_(group_ids))),
                                                            Image.creator_id == current_user.id))
                                                .all())
        images_exclude_ids = Image.query.with_entities(Image.image_hash).filter(
            or_(Image.access.has(Access.name == 'none'),
                and_(Image.access.has(Access.name == 'group'),
                     Image.groups.any(~Group.id.in_(group_ids))))).all()
        reverse = False
    else:
        images_in_db_dict = image_query_to_dict(Image.query.with_entities(Image.image_hash, Image)
                                                .filter(or_(Image.access.has(Access.name == 'all'),
                                                            and_(Image.access.has(Access.name == 'group'),
                                                                 Image.groups.any(Group.id.in_(group_ids))),
                                                            Image.creator_id == current_user.id))
                                                .all())
        images_exclude_ids = []
        reverse = True
    images_in_docker = merge_image_info(images_in_docker, images_in_db_dict, images_exclude_ids, reverse)
    return images_in_docker


def merge_image_info(images_in_docker, images_in_db_dict, images_exclude_ids=(), reverse=False):
    new_images_in_docker = []
    for image in images_in_docker:
        if image.attrs['Id'] in images_exclude_ids or (reverse and image.attrs['Id'] not in images_in_db_dict):
            continue
        if image.attrs['Id'] in list(images_in_db_dict.keys()):
            image.is_in_db = True
            image.creator = images_in_db_dict[image['id']].creator.username
            image.action = images_in_db_dict[image['id']].creator_id == current_user.id
        else:
            image.is_in_db = False
            image.creator = ''
            image.action = current_user.role.name == 'super'
        new_images_in_docker.append(image)
    return new_images_in_docker


def image_query_to_dict(images_list):
    images_dict = dict()
    for k, v in images_list:
        images_dict[k] = v
    return images_dict


def handle_image_pull_name(name):
    if len(name.split('/')) == 1:
        name = 'library/' + name
    if len(name.split(':')) == 1:
        name = name + ':latest'
    return name.split(':')


def pull_image(endpoint_id, form):
    endpoint = Endpoint.query.get(endpoint_id)
    name = form.name.data
    url = Registry.query.get(form.registry.data).url
    repo, tag = handle_image_pull_name(name)
    repo = '%s/%s' % (url, repo)
    try:
        client = docker_client(endpoint.url)
        current_app.logger.info('Start to pull image: %s:%s, user: %s' % (repo, tag, current_user.username))
        image = client.images.pull(repo, tag)
        save_pulled_image_to_db(image)
        return image
    except (DockerException, APIError) as ex:
        current_app.logger.error('Pull image: %s:%s fail, error: %s, user: %s' % (repo, tag, ex, current_user.username))
        return None


def save_pulled_image_to_db(image):
    image_hash = image.attrs['Id']
    image_db = Image.query.filter(Image.image_hash == image_hash).first()
    if image_db:
        return image_db
    image_db = Image()
    image_db.image_hash = image_hash
    if 'library' in image.tags[0]:
        image_db.creator_id = User.query.filter(User.role.has(Role.name == 'super')).first().id
    else:
        image_db.creator_id = current_user.id
    if current_user.role.name == 'super':
        image_db.access = Access.query.filter(Access.name == 'all')
    else:
        image_db.access = Access.query.filter(Access.name == 'group')
    try:
        db.session.ad(image_db)
        db.session.commit()
        return image_db
    except Endpoint as ex:
        db.session.rollback()
        current_app.logger.error(
            'save pulled image: <%s> to db fail, error: %s, user: %s' % (image.attrs['Id'], ex, current_user.username))
        return None


def remove_images(endpoint_id, image_hashs):
    url = Endpoint.query.get(endpoint_id).url
    try:
        client = docker_client(url)
    except DockerException as ex:
        current_app.logger.error('Cannot connect to docker server: %s' % url)
        return False
    images_in_db = dict()
    for k, v in Image.query.with_entities(Image.image_hash, Image).filter(Image.image_hash.in_(image_hashs)).all():
        images_in_db[k] = v
    fail_list = []
    for image_hash in image_hashs:
        try:
            client.images.remove(image=image_hash)
        except APIError as ex:
            current_app.logger.error('Fail to remove image: %s, error: %s, user: %s',
                                     (image_hash, ex, current_user.username))
            fail_list.append(image_hash)
            continue
        image_in_db = images_in_db.get(image_hash, None)
        if image_in_db:
            db.session.remove(image_in_db)
    db.session.commit()
    if 0 < len(fail_list):
        return fail_list
    return True
