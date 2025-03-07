"""Add sasl logs

Revision ID: cf1ffc14619b
Revises: 359478dc9830
Create Date: 2025-02-17 20:13:26.437886

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "cf1ffc14619b"
down_revision: str | None = "359478dc9830"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "sasl_log",
        sa.Column("app_password", sa.Integer(), nullable=False),
        sa.Column("service", sa.String(length=32), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=False),
        sa.Column("real_ip", sa.String(length=64), nullable=False),
        sa.Column("datetime", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("service", "real_ip", "username"),
    )
    op.create_index("sasl_log_datetime_key", "sasl_log", ["datetime"], unique=False)
    op.create_index("sasl_log_real_ip_key", "sasl_log", ["real_ip"], unique=False)
    op.create_index("sasl_log_service_key", "sasl_log", ["service"], unique=False)
    op.create_index("sasl_log_username_key", "sasl_log", ["username"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("sasl_log_username_key", table_name="sasl_log")
    op.drop_index("sasl_log_service_key", table_name="sasl_log")
    op.drop_index("sasl_log_real_ip_key", table_name="sasl_log")
    op.drop_index("sasl_log_datetime_key", table_name="sasl_log")
    op.drop_table("sasl_log")
    # ### end Alembic commands ###
