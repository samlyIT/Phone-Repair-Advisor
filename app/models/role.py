from app import db
from app.models.associations import role_permissions


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))

    # Relationships
    permissions = db.relationship(
        'Permission',
        secondary=role_permissions,
        backref='roles')

    def __repr__(self):
        return f'<Role {self.name}>'

    @staticmethod
    def insert_roles():
        roles = {
            'User': ['submit_request'],
            'Technician': ['view_requests', 'update_status'],
            'Admin': ['admin_access', 'manage_users', 'view_all_requests']
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            for perm_name in roles[r]:
                permission = Permission.query.filter_by(name=perm_name).first()
                if permission is None:
                    permission = Permission(name=perm_name)
                    db.session.add(permission)
                if permission not in role.permissions:
                    role.permissions.append(permission)
            db.session.add(role)
        db.session.commit()


class Permission(db.Model):
    __tablename__ = 'permissions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))

    def __repr__(self):
        return f'<Permission {self.name}>'
