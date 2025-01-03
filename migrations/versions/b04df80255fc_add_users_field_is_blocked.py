"""Add users field is_blocked

Revision ID: b04df80255fc
Revises: 30fb493e6cd0
Create Date: 2023-09-27 11:47:02.874196

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b04df80255fc"
down_revision: Union[str, None] = "30fb493e6cd0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("users", sa.Column("is_blocked", sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "is_blocked")
    # ### end Alembic commands ###
