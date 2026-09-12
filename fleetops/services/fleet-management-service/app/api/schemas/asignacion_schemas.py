from uuid import UUID

from pydantic import BaseModel


class AsignacionRequest(BaseModel):
    conductor_id: UUID
