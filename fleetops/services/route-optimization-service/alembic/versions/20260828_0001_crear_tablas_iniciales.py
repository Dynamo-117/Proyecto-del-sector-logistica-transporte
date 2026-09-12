"""crear tablas iniciales: nodos, aristas, cargas, rutas, vehiculos_disponibles

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
        "nodos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("nombre", sa.String(length=120), nullable=False),
        sa.Column("latitud", sa.Float(), nullable=False),
        sa.Column("longitud", sa.Float(), nullable=False),
    )

    op.create_table(
        "aristas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("nodo_origen_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("nodos.id"), nullable=False),
        sa.Column("nodo_destino_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("nodos.id"), nullable=False),
        sa.Column("distancia_km", sa.Float(), nullable=False),
    )

    op.create_table(
        "cargas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("origen_nodo_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("nodos.id"), nullable=False),
        sa.Column("destino_nodo_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("nodos.id"), nullable=False),
        sa.Column("peso_kg", sa.Float(), nullable=False),
        sa.Column("volumen_m3", sa.Float(), nullable=False),
        sa.Column("estado", sa.String(length=20), nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "rutas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("carga_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cargas.id"), nullable=False),
        sa.Column("vehiculo_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("nodos", sa.JSON(), nullable=False),
        sa.Column("distancia_km", sa.Float(), nullable=False),
        sa.Column("estado", sa.String(length=20), nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_rutas_vehiculo_id", "rutas", ["vehiculo_id"])

    op.create_table(
        "vehiculos_disponibles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("placa", sa.String(length=20), nullable=False),
        sa.Column("capacidad_kg", sa.Float(), nullable=False),
        sa.Column("estado", sa.String(length=20), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("vehiculos_disponibles")
    op.drop_index("ix_rutas_vehiculo_id", table_name="rutas")
    op.drop_table("rutas")
    op.drop_table("cargas")
    op.drop_table("aristas")
    op.drop_table("nodos")
