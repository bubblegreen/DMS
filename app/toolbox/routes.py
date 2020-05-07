from app.toolbox import bp
from flask_login import login_required, current_user
from flask import request, session, render_template, jsonify, current_app
from app.toolbox.forms import DockerServerForm
from app.toolbox import services
from app.endpoint.services import get_all_endpoint_from_db
from app.group.services import get_all_groups
from app.image.services import get_images_tag_list
from app.volume.services import get_volumes
from app.network.services import get_networks, join_container, get_network_by_name


@bp.route('/container-batch')
@login_required
def index():
    permission = current_user.permission_info.get('container', None)
    permission = permission.permission_type if permission else ''
    form = DockerServerForm()
    form.servers.choices = list((e.id, e.name) for e in get_all_endpoint_from_db())

    return render_template('toolbox/container-batch.html', permission=permission)
