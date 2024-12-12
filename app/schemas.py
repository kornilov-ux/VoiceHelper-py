from pydantic import BaseModel

class AudioFileBase(BaseModel):
    file_path: str

class AudioFileCreate(AudioFileBase):
    pass

class AudioFile(AudioFileBase):
    id: int

    class Config:
        orm_mode = True
