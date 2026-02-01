"""seed roles and permissions

Revision ID: 09b03f1a8343
Revises: 9c627519532f
Create Date: 2025-12-17 14:32:08.861937

"""
from alembic import op
import sqlalchemy as sa
from werkzeug.security import generate_password_hash
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '09b03f1a8343'
down_revision = '9c627519532f'
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
