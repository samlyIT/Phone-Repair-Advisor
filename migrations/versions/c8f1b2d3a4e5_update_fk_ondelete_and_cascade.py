"""Update foreign keys: repairs.issue_id ON DELETE CASCADE, rules.repair_id ON DELETE SET NULL

Revision ID: c8f1b2d3a4e5
Revises: 635b901b91fd
Create Date: 2026-01-05 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'c8f1b2d3a4e5'
down_revision = '635b901b91fd'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # --- repairs.issue_id -> add ON DELETE CASCADE ---
    try:
        fks = inspector.get_foreign_keys('repairs')
        for fk in fks:
            if fk.get('referred_table') == 'issues':
                fk_name = fk.get('name')
                if fk_name:
                    op.drop_constraint(fk_name, 'repairs', type_='foreignkey')
                # create new FK with ON DELETE CASCADE
                op.create_foreign_key('fk_repairs_issue_id_issues', 'repairs', 'issues', ['issue_id'], ['id'], ondelete='CASCADE')
                break
    except Exception:
        # Best-effort: if we can't introspect, attempt to (re)create FK
        op.create_foreign_key('fk_repairs_issue_id_issues', 'repairs', 'issues', ['issue_id'], ['id'], ondelete='CASCADE')

    # --- rules.repair_id -> add ON DELETE SET NULL ---
    try:
        fks = inspector.get_foreign_keys('rules')
        for fk in fks:
            if fk.get('referred_table') == 'repairs':
                fk_name = fk.get('name')
                if fk_name:
                    op.drop_constraint(fk_name, 'rules', type_='foreignkey')
                op.create_foreign_key('fk_rules_repair_id_repairs', 'rules', 'repairs', ['repair_id'], ['id'], ondelete='SET NULL')
                break
    except Exception:
        op.create_foreign_key('fk_rules_repair_id_repairs', 'rules', 'repairs', ['repair_id'], ['id'], ondelete='SET NULL')


def downgrade():
    # Reverse changes: drop named constraints and recreate without ondelete
    try:
        op.drop_constraint('fk_repairs_issue_id_issues', 'repairs', type_='foreignkey')
    except Exception:
        pass
    op.create_foreign_key(None, 'repairs', 'issues', ['issue_id'], ['id'])

    try:
        op.drop_constraint('fk_rules_repair_id_repairs', 'rules', type_='foreignkey')
    except Exception:
        pass
    op.create_foreign_key(None, 'rules', 'repairs', ['repair_id'], ['id'])
