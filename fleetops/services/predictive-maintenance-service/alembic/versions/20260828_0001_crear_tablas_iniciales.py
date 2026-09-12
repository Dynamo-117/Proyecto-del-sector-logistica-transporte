"""crear tablas iniciales: vehiculos_conocidos, lecturas_odometro, estados_mantenimiento, alertas

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
        "vehiculos_conocidos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("placa", sa.String(length=20), nullable=False),
    )

    op.create_table(
        "lecturas_odometro",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("vehiculo_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("kilometraje_km", sa.Float(), nullable=False),
        sa.Column("horas_motor", sa.Float(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_lecturas_odometro_vehiculo_id", "lecturas_odometro", ["vehiculo_id"])

    op.create_table(
        "estados_mantenimiento",
        sa.Column("vehiculo_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tipo", sa.String(length=30), primary_key=True),
        sa.Column("km_base", sa.Float(), nullable=False, server_default="0"),
        sa.Column("horas_base", sa.Float(), nullable=False, server_default="0"),
    )

    op.create_table(
        "alertas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("vehiculo_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tipo", sa.String(length=30), nullable=False),
        sa.Column("estado", sa.String(length=20), nullable=False),
        sa.Column("kilometraje_km", sa.Float(), nullable=False),
        sa.Column("horas_motor", sa.Float(), nullable=False),
        sa.Column("generada_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("resuelta_en", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_alertas_vehiculo_id", "alertas", ["vehiculo_id"])


def downgrade() -> None:
    op.drop_index("ix_alertas_vehiculo_id", table_name="alertas")
    op.drop_table("alertas")
    op.drop_table("estados_mantenimiento")
    op.drop_index("ix_lecturas_odometro_vehiculo_id", table_name="lecturas_odometro")
    op.drop_table("lecturas_odometro")
    op.drop_table("vehiculos_conocidos")
