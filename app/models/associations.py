from app import db

# Many-to-many: Role <-> Permission
role_permissions = db.Table('role_permissions',
                            db.Column(
                                'role_id',
                                db.Integer,
                                db.ForeignKey('roles.id'),
                                primary_key=True),
                            db.Column(
                                'permission_id',
                                db.Integer,
                                db.ForeignKey('permissions.id'),
                                primary_key=True)
                            )

# Many-to-many: Issue <-> Symptom
issue_symptoms = db.Table('issue_symptoms',
                          db.Column(
                              'issue_id',
                              db.Integer,
                              db.ForeignKey('issues.id'),
                              primary_key=True),
                          db.Column(
                              'symptom_id',
                              db.Integer,
                              db.ForeignKey('symptoms.id'),
                              primary_key=True)
                          )
