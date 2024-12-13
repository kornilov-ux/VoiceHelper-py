from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import AudioFile


def inspect_database():
    # Создаем сессию
    db: Session = SessionLocal()
    try:
        # Выполняем запрос для получения всех записей из таблицы audio_files
        audio_files = db.query(AudioFile).all()
        if audio_files:
            print("Содержимое таблицы audio_files:")
            for audio in audio_files:
                print(f"ID: {audio.id}, File Path: {audio.file_path}")
        else:
            print("Таблица audio_files пуста.")
    except Exception as e:
        print(f"Ошибка при подключении к базе данных: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    inspect_database()
