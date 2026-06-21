from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from pgvector.sqlalchemy import Vector


base = declarative_base()

class Job(base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    company = Column(String)
    description = Column(Text)                       
    location = Column(String)
    url         = Column(String, unique=True, nullable=False)
    source = Column(String)  
    created     = Column(DateTime)                     
    embedding   = Column(Vector(384), nullable=True)