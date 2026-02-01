"""Set issues.phone_id FK ON DELETE CASCADE

Revision ID: d9e3f4a5b6c7
Revises: c8f1b2d3a4e5
Create Date: 2026-01-05 16:20:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'd9e3f4a5b6c7'
down_revision = 'c8f1b2d3a4e5'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    try:
        fks = inspector.get_foreign_keys('issues')
        for fk in fks:
            if fk.get('referred_table') == 'phones':
                fk_name = fk.get('name')
                if fk_name:
                    op.drop_constraint(fk_name, 'issues', type_='foreignkey')
                op.create_foreign_key('fk_issues_phone_id_phones', 'issues', 'phones', ['phone_id'], ['id'], ondelete='CASCADE')
                break
    except Exception:
        op.create_foreign_key('fk_issues_phone_id_phones', 'issues', 'phones', ['phone_id'], ['id'], ondelete='CASCADE')


def downgrade():
    try:
        op.drop_constraint('fk_issues_phone_id_phones', 'issues', type_='foreignkey')
    except Exception:
        pass
    op.create_foreign_key(None, 'issues', 'phones', ['phone_id'], ['id'])
