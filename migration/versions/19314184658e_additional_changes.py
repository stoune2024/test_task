"""additional_changes

Revision ID: 19314184658e
Revises: 1c2e3c821ef8
Create Date: 2025-07-25 16:58:39.136685

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '19314184658e'
down_revision: Union[str, Sequence[str], None] = '1c2e3c821ef8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('walletbalance', sa.Column('additional_info', sqlmodel.sql.sqltypes.AutoString(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('walletbalance', 'additional_info')
    # ### end Alembic commands ###
