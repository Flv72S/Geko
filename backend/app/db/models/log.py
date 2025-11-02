from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.db.base import Base


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    evento = Column(String(100))
    descrizione = Column(Text)
    livello = Column(String(20), default="INFO")
    created_at = Column(DateTime, default=datetime.utcnow)

