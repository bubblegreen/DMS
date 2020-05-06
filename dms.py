from app import create_app, db
from app.models import User, Role, Permission, Group, Endpoint, Access, Image
import cli

app = create_app()
cli.register(app)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Role': Role, 'Permisson': Permission, 'Group': Group, 'Endpoint': Endpoint,
            'Access': Access, 'Image': Image}
