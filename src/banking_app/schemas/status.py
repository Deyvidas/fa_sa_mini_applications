from src.banking_app.schemas.base import Base


class StatusDescDTO(Base):
    status: int
    description: str
