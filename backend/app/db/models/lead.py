from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from datetime import datetime
from app.db.base import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    azienda_id = Column(Integer, ForeignKey("aziende.id"))
    nome_contatto = Column(String(100))
    ruolo = Column(String(100))
    email = Column(String(100))
    telefono = Column(String(50))
    punteggio = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

