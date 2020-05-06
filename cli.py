def register(app):
    @app.cli.group()
    def generate():
        pass

    @generate.command()
    def init():
        from app.models import User, Registry, Access, Permission, Role
        from app import db
        role1 = Role(name='super')
        role2 = Role(name='group')
        role3 = Role(name='norm')
        db.session.add_all([role1, role2, role3])
        db.session.flush()

        access1 = Access(name='none')
        access2 = Access(name='group')
        access3 = Access(name='all')
        db.session.add_all([access1, access2, access3])
        db.session.flush()

        per1 = Permission(name='image', permission_type='view', value=1)
        per2 = Permission(name='image', permission_type='pull', value=2)
        per3 = Permission(name='image', permission_type='create', value=3)
        per4 = Permission(name='image', permission_type='push', value=4)
        per5 = Permission(name='container', permission_type='view', value=1)
        per6 = Permission(name='container', permission_type='create', value=2)
        per7 = Permission(name='network', permission_type='view', value=1)
        per8 = Permission(name='network', permission_type='create', value=2)
        per9 = Permission(name='volume', permission_type='view', value=1)
        per10 = Permission(name='volume', permission_type='create', value=2)
        per11 = Permission(name='endpoint', permission_type='view', value=1)
        per12 = Permission(name='endpoint', permission_type='create', value=2)
        per13 = Permission(name='registry', permission_type='view', value=1)
        per14 = Permission(name='registry', permission_type='create', value=2)
        db.session.add_all([per1, per2, per3, per4, per5, per6, per7, per8, per9, per10, per11, per12, per13, per14])
        db.session.flush()

        user = User(email='xuhang@aisino.com', role=role1, permissions=[per4, per6, per8, per10, per12, per14], active=1)
        user.set_password('Xu810823')
        db.session.add(user)
        db.session.flush()

        r1 = Registry(name='DockerHub', url='', access=access3, creator_id=user.id)
        r2 = Registry(name='163Registry', url='hub.c.163.com', access=access3, creator_id=user.id)
        db.session.add_all([r1, r2])
        db.session.commit()
