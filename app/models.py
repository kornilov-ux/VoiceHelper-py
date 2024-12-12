from sqlalchemy import Column, Integer, String
from app.database import Base

class AudioFile(Base):
    __tablename__ = "audio_files"
    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, index=True)
