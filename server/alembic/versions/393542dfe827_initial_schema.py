"""initial_schema

Revision ID: 393542dfe827
Revises:
Create Date: 2025-10-27 13:32:44.836173

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "393542dfe827"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	"""Upgrade schema."""
	# Create urls table (without created_at - representing current database state)
	op.create_table(
		"urls",
		sa.Column("id", sa.Integer(), nullable=False),
		sa.Column("key", sa.String(), nullable=True),
		sa.Column("secret_key", sa.String(), nullable=True),
		sa.Column("target_url", sa.String(), nullable=True),
		sa.Column("is_active", sa.Boolean(), nullable=True),
		sa.Column("clicks", sa.Integer(), nullable=True),
		sa.PrimaryKeyConstraint("id"),
	)
	op.create_index(op.f("ix_urls_key"), "urls", ["key"], unique=True)
	op.create_index(
		op.f("ix_urls_secret_key"), "urls", ["secret_key"], unique=True
	)
	op.create_index(
		op.f("ix_urls_target_url"), "urls", ["target_url"], unique=False
	)


def downgrade() -> None:
	"""Downgrade schema."""
	op.drop_index(op.f("ix_urls_target_url"), table_name="urls")
	op.drop_index(op.f("ix_urls_secret_key"), table_name="urls")
	op.drop_index(op.f("ix_urls_key"), table_name="urls")
	op.drop_table("urls")
