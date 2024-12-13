from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import engine, get_db
from app.audio import transcribe_audio
from app.config import UPLOAD_DIRECTORY, AUTH_KEY_VALUE
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
import shutil
import os
import logging


# Инициализация приложения
app = FastAPI()

# Создание таблиц в базе данных
models.Base.metadata.create_all(bind=engine)

# Инициализация логирования
logging.basicConfig(level=logging.INFO)

# Базовый маршрут
@app.get("/")
def read_root():
    return {"message": "Welcome to VoiceHelper API!"}


# Эндпоинт для загрузки аудиофайлов и обработки их с помощью Vosk
@app.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...), db: Session = Depends(get_db)):
    logging.info(f"Получен файл с MIME-типом: {file.content_type}")
    # Проверка существования директории для сохранения файлов
    os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

    # Путь к файлу на диске
    file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)

    # Сохраняем файл на диск
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Используем Vosk для транскрипции аудио
    text = transcribe_audio(file_path)

    # Сохраняем информацию о файле в базе данных
    audio_entry = models.AudioFile(file_path=file_path)
    db.add(audio_entry)
    db.commit()
    db.refresh(audio_entry)

    # return {"id": audio_entry.id, "file_path": audio_entry.file_path, "transcription": text}
    # передаем текст в GigaChat и получаем ответ
    try:
        # Подготовка данных для GigaChat
        payload = Chat(
            messages=[
                Messages(
                    role=MessagesRole.USER,
                    content=text  # Передаем текст, полученный из Vosk
                )
            ],
            temperature=0.7,
            max_tokens=100,
        )

        # Использование GigaChat API для получения ответа
        with GigaChat(credentials=AUTH_KEY_VALUE, verify_ssl_certs=False) as giga:
            response = giga.chat(payload)
            # Возвращаем ответ GigaChat
            return {"id": audio_entry.id, "file_path": audio_entry.file_path, "transcription": text,
                    "response": response.choices[0].message.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обработке запроса: {str(e)}")









# Эндпоинт для отправки транскрибированного текста в GigaChat
# @app.post("/process-text/{audio_id}")
# async def process_text(audio_id: int, db: Session = Depends(get_db)):
#     try:
#         # Получаем запись из базы данных по ID
#         audio_entry = db.query(models.AudioFile).filter(models.AudioFile.id == audio_id).first()
#
#         if not audio_entry:
#             raise HTTPException(status_code=404, detail="Audio file not found")
#
#         # Подготовка данных для GigaChat
#         payload = Chat(
#             messages=[
#                 Messages(
#                     role=MessagesRole.USER,
#                     content=audio_entry.transcription  # Используем расшифрованный текст
#                 )
#             ],
#             temperature=0.7,
#             max_tokens=100,
#         )
#
#         # Использование GigaChat API для получения ответа
#         with GigaChat(credentials=AUTH_KEY_VALUE, verify_ssl_certs=False) as giga:
#             response = giga.chat(payload)
#
#             return {"response": response.choices[0].message.content}
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Ошибка при обработке запроса: {str(e)}")
#