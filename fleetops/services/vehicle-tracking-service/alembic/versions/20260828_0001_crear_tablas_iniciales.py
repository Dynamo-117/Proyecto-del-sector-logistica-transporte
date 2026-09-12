"""crear tablas iniciales: vehiculos_conocidos y telemetria (hypertable)

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
        sa.Column("registrado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "telemetria",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("vehiculo_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("latitud", sa.Float(), nullable=False),
        sa.Column("longitud", sa.Float(), nullable=False),
        sa.Column("velocidad_kmh", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("timestamp", "vehiculo_id"),
    )
    op.create_index("ix_telemetria_vehiculo_id", "telemetria", ["vehiculo_id"])

    # TimescaleDB convierte 'telemetria' en hypertable (particionamiento
    # automatico por tiempo, pensado para series de tiempo a gran escala).
    # Es opcional a proposito: si la extension no esta instalada o falla al
    # cargar (algunos entornos Windows tienen un bug conocido del DLL de
    # TimescaleDB sin solucion oficial todavia, ver README de este servicio),
    # 'telemetria' se queda como tabla normal de Postgres. La aplicacion
    # funciona igual en ambos casos -- solo cambia si hay particionamiento
    # automatico por debajo, invisible para el resto del codigo.
    conn = op.get_bind()
    try:
        with conn.begin_nested():
            conn.execute(sa.text("CREATE EXTENSION IF NOT EXISTS timescaledb"))
            conn.execute(
                sa.text(
                    "SELECT create_hypertable('telemetria', 'timestamp', if_not_exists => TRUE)"
                )
            )
    except Exception as exc:
        print(
            f"AVISO: TimescaleDB no disponible ({exc}). "
            "'telemetria' queda como tabla normal de Postgres."
        )


def downgrade() -> None:
    op.drop_index("ix_telemetria_vehiculo_id", table_name="telemetria")
    op.drop_table("telemetria")
    op.drop_table("vehiculos_conocidos")
