from dataclasses import dataclass
from uuid import UUID

@dataclass
class User:
    id: UUID
    name: str
    surname: str
    farthername: str
    role: str
    tg_id: str
    username: str
    area: str | None
    team: str




