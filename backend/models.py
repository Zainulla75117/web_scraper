from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    url = Column(String, index=True)
    path = Column(String)
    section = Column(String)
    category = Column(String)
    subcategory = Column(String)
    title = Column(String)
    source = Column(String, default="kubernetes.io")
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")

class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(String, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("documents.id"))
    chunk_index = Column(Integer)
    content = Column(Text)

    document = relationship("Document", back_populates="chunks")
