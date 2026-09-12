"""crear tablas iniciales: vehiculos y conductores

Revision ID: 0001
Revises:
Create Date: 2026-08-28

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "conductores",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("nombre", sa.String(length=120), nullable=False),
        sa.Column("licencia", sa.String(length=30), nullable=False),
        sa.Column("estado", sa.String(length=20), nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("actualizado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_conductores_licencia", "conductores", ["licencia"], unique=True)

    op.create_table(
        "vehiculos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("placa", sa.String(length=20), nullable=False),
        sa.Column("tipo", sa.String(length=20), nullable=False),
        sa.Column("capacidad_kg", sa.Float(), nullable=False),
        sa.Column("estado", sa.String(length=20), nullable=False),
        sa.Column(
            "conductor_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("conductores.id"),
            nullable=True,
        ),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("actualizado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_vehiculos_placa", "vehiculos", ["placa"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_vehiculos_placa", table_name="vehiculos")
    op.drop_table("vehiculos")
    op.drop_index("ix_conductores_licencia", table_name="conductores")
    op.drop_table("conductores")
