from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.db.base import Base


class Azienda(Base):
    __tablename__ = "aziende"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    settore = Column(String(100))
    sito_web = Column(String(255))
    paese = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

