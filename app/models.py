from sqlalchemy import Column, Integer, String
from app.database import Base
from pydantic import BaseModel


class AudioFile(Base):
    __tablename__ = "audio_files"
    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, index=True)


class TextRequest(BaseModel):
    input_text: str
