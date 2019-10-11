from docker.errors import DockerException, APIError, BuildError
from app.models import Image, Group, Endpoint, Access, User, Role, Registry
from flask_login import current_user
from app.utils.docker import docker_client, merge_info, get_entities_with_authority
from sqlalchemy import or_, and_
from app import db
from flask import current_app, request
import tempfile
import os
import shutil
from werkzeug.utils import secure_filename
import tarfile
from git import Repo
from git.exc import GitCommandError


def get_images(endpoint_id):
    role = current_user.role.name
    endpoint = Endpoint.query.get(endpoint_id)
    try:
        client = docker_client(endpoint.url)
    except (DockerException, APIError) as ex:
        current_app.logger.error(ex)
        return []
    images_in_docker = client.images.list()
    return get_entities_with_authority(role, Image, images_in_docker)


def get_images_tag_list(endpoint_id):
    images = get_images(endpoint_id)
    tag_list = []
    for image in images:
        image_hash = image.id
        for tag in image.tags:
            tag_list.append((image_hash, tag))
    return tag_list


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
    repo = ('%s/%s' % (url, repo)) if url != '' else repo.replace('library/', '')
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
    hash = image.attrs['Id']
    image_db = Image.query.filter(Image.hash == hash).first()
    if image_db:
        return image_db
    image_db = Image()
    image_db.hash = hash
    if 'library' in image.tags[0]:
        image_db.creator_id = User.query.filter(User.role.has(Role.name == 'super')).first().id
    else:
        image_db.creator_id = current_user.id
    if current_user.role.name == 'super':
        image_db.access = Access.query.filter(Access.name == 'all')
    else:
        image_db.access = Access.query.filter(Access.name == 'group')
    try:
        db.session.add(image_db)
        db.session.commit()
        return image_db
    except Exception as ex:
        db.session.rollback()
        current_app.logger.error(
            'save pulled image: <%s> to db fail, error: %s, user: %s' % (image.attrs['Id'], ex, current_user.username))
        return None


def remove_images(endpoint_id, hashs):
    url = Endpoint.query.get(endpoint_id).url
    try:
        client = docker_client(url)
    except DockerException as ex:
        current_app.logger.error('Cannot connect to docker server: %s' % url)
        return False
    images_in_db = dict()
    for k, v in Image.query.with_entities(Image.hash, Image).filter(Image.hash.in_(hashs)).all():
        images_in_db[k] = v
    fail_list = []
    for hash in hashs:
        try:
            client.images.remove(image=hash)
        except APIError as ex:
            current_app.logger.error('Fail to remove image: %s, error: %s, user: %s',
                                     (hash, ex, current_user.username))
            fail_list.append(hash)
            continue
        image_in_db = images_in_db.get(hash, None)
        if image_in_db:
            db.session.delete(image_in_db)
    db.session.commit()
    if 0 < len(fail_list):
        return fail_list
    return True


def build_image(endpoint_id, form):
    current_app.logger.info('enter build image service')
    endpoint = Endpoint.query.get(endpoint_id)
    tag = form.name.data
    groups = Group.query.filter(Group.id.in_(form.groups.data)).all()
    access_id = form.access.data
    method = form.method.data
    image_db = Image()
    image_db.groups = groups
    image_db.access_id = access_id
    image_db.creator_id = current_user.id
    if method == 'editor':
        if form.code.data == '':
            form.code.errors.append('Dockerfile内容不能为空!')
            return form
        else:
            d = None
            try:
                d = tempfile.mkdtemp(dir=current_app.config['UPLOAD_FOLDER'])
                with open(os.path.join(d, 'Dockerfile'), 'w') as f:
                    content = 'FROM %s\n%s' % (form.base_image.data, form.code.data)
                    current_app.logger.info(content)
                    f.write(content)
                client = docker_client(endpoint.url)
                labels = {'Author': current_user.email}
                image, logs = client.images.build(path=d, tag=tag, labels=labels)
                image_db.hash = image.attrs['Id']
                db.session.add(image_db)
                db.session.commit()
                return image
            except (DockerException, BuildError, APIError, PermissionError) as ex:
                current_app.logger.error(ex)
                form.code.errors.append(ex)
                return form
            finally:
                if d:
                    shutil.rmtree(d)
    elif method == 'upload':
        if form.file.data == '':
            form.file.errors.append('请上传tar文件!')
            return form
        else:
            d = None
            file = request.files[form.file.name]
            current_app.logger.info(file.filename)
            filename = secure_filename(file.filename)
            try:
                d = tempfile.mkdtemp(dir=current_app.config['UPLOAD_FOLDER'])
                filepath = os.path.join(d, filename)
                file.save(filepath)
                if not tarfile.is_tarfile(filepath):
                    form.file.errors.append('请上传tar格式文件!')
                    return form
                with tarfile.open(filepath, 'r') as tar:
                    extra_path = os.path.join(d, filename[:filename.rindex('.')])
                    tar.extractall(extra_path)
                if os.path.exists(os.path.join(extra_path, 'Dockerfile')):
                    dockerfile = os.path.join(extra_path, 'Dockerfile')
                else:
                    form.file.errors.append('tar根目录中必须包含Dockerfile文件!')
                    return form
                # todo validate 'FROM' statement of dockerfile
                if not validate_dockerfile(dockerfile, endpoint_id):
                    form.file.errors.append('Dockerfile中，只能引入已有的镜像!')
                    return form
                client = docker_client(endpoint.url)
                labels = {'Author': current_user.email}
                image, logs = client.images.build(path=extra_path, tag=tag, labels=labels)
                image_db.hash = image.attrs['Id']
                db.session.add(image_db)
                db.session.commit()
                return image
            except (DockerException, BuildError, APIError, PermissionError) as ex:
                current_app.logger.error(ex)
                form.file.errors.append(ex)
                return form
            finally:
                if d:
                    shutil.rmtree(d)
    else:
        if form.url.data == '':
            form.url.errors.append('请输入Git URL地址!')
        else:
            git_url = form.url.data
            d = None
            try:
                d = tempfile.mkdtemp(dir=current_app.config['UPLOAD_FOLDER'])
                Repo.clone_from(git_url, d)
                if os.path.exists(os.path.join(d, 'Dockerfile')):
                    dockerfile = os.path.join(d, 'Dockerfile')
                else:
                    form.url.errors.append('Dockerfile文件必须在项目根目录中')
                    return form
                # validate 'FROM' statement of dockerfile
                if not validate_dockerfile(dockerfile, endpoint_id):
                    form.url.errors.append('Dockerfile中，只能引入已有的镜像!')
                    return form
                client = docker_client(endpoint.url)
                labels = {'Author': current_user.email}
                image, logs = client.images.build(path=d, tag=tag, labels=labels)
                image_db.hash = image.attrs['Id']
                db.session.add(image_db)
                db.session.commit()
                return image
            except (DockerException, BuildError, APIError, PermissionError, GitCommandError) as ex:
                current_app.logger.error(ex)
                form.url.errors.append(ex)
                return form
            finally:
                if d:
                    shutil.rmtree(d)


def validate_dockerfile(dockerfile, endpoint_id):
    with open(dockerfile, 'r') as f:
        for line in f.readlines():
            if 'from' in line.lower():
                statement = line.strip()
                base_image_name = statement[4:].strip()
                images = get_images(endpoint_id)
                for image in images:
                    if base_image_name in image.tags:
                        return True
    return False


def get_image_by_id(endpoint_id, hash):
    endpoint = Endpoint.query.get(endpoint_id)
    try:
        client = docker_client(endpoint.url)
        image = client.images.get(hash)
        size = '%.1f' % (image.attrs['Size'] / 1000 / 1000)
        if len(size[:size.index('.')]) <= 3:
            size = size.replace('.0', '') + 'MB'
        else:
            size = '%.1f' % (image.attrs['Size'] / 1000 / 1000 / 1000)
            size = size.replace('.0', '') + 'GB'
        image.attrs['Size'] = size
        create = image.attrs['Created']
        create = create[:create.index('.')].replace('T', ' ')
        image.attrs['Created'] = create
        image_db = Image.query.filter(Image.hash == hash).first()
        if image_db:
            image.db = image_db
        else:
            image.db = None
        return image
    except (DockerException, APIError) as ex:
        current_app.logger.error(ex)


def tag_image(endpoint_id, hash, form):
    endpoint = Endpoint.query.get(endpoint_id)
    try:
        client = docker_client(endpoint.url)
        image = client.images.get(hash)
        name = form.name.data
        url = Registry.query.get(form.registry.data).url
        repo, tag = handle_image_pull_name(name)
        repo = ('%s/%s' % (url, repo)) if url != '' else repo.replace('library/', '')
        image.tag(repo, tag)
        return image
    except (DockerException, APIError) as ex:
        current_app.logger.error(ex)
        return ex


def get_image_tag_list(endpoint_id, hash):
    endpoint = Endpoint.query.get(endpoint_id)
    try:
        client = docker_client(endpoint.url)
        image = client.images.get(hash)
        return image.tags
    except (DockerException, APIError) as ex:
        current_app.logger.error(ex)
        return []


def untag_image(endpoint_id, tag):
    endpoint = Endpoint.query.get(endpoint_id)
    try:
        client = docker_client(endpoint.url)
        current_app.logger.info(tag)
        client.images.remove(image=tag)
        return 'ok'
    except (DockerException, APIError) as ex:
        current_app.logger.error(ex)
        return None


def update_image(hash, form):
    try:
        image_in_db = Image.query.filter(Image.hash == hash).first()
        groups = Group.query.filter(Group.id.in_(form.groups.data)).all()
        access_id = form.access.data
        if not image_in_db:
            image_in_db = Image()
            image_in_db.hash = hash
            image_in_db.creator_id = current_user.id
            db.session.add(image_in_db)
        image_in_db.groups = groups
        image_in_db.access_id = access_id
        db.session.commit()
        return 'ok'
    except Exception as ex:
        current_app.logger.error(ex)
        return ex
