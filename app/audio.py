from vosk import Model, KaldiRecognizer
from pydub import AudioSegment
from app.config import VOSK_MODEL_PATH
import wave
import os
import json
import ffmpeg
import logging


def convert_mp3_to_wav(mp3_path: str, wav_path: str):
    """Конвертация MP3 в WAV с использованием ffmpeg-python"""
    logging.info(f"Конвертация MP3 в WAV: {mp3_path} -> {wav_path}")
    try:
        ffmpeg.input(mp3_path).output(wav_path, ac=1, ar='16000').run()
        logging.info(f"Конвертация завершена: {wav_path}")
    except Exception as e:
        logging.error(f"Ошибка при конвертации {mp3_path} в {wav_path}: {e}")
        raise ValueError(f"Ошибка при конвертации {mp3_path} в {wav_path}")


def ensure_wav_format(wav_path: str, output_path: str):
    """Приведение аудиофайла к формату: моно, 16-бит, 16000 Гц"""
    try:
        ffmpeg.input(wav_path).output(output_path, ac=1, ar='16000', sample_fmt='s16').run()
        logging.info(f"Аудиофайл приведен к формату: {output_path}")
    except Exception as e:
        logging.error(f"Ошибка при преобразовании аудиофайла {wav_path}: {e}")
        raise ValueError(f"Ошибка при преобразовании аудиофайла {wav_path}")


def transcribe_audio(file_path: str) -> str:
    formatted_wav_path = None
    try:
        logging.info(f"Начинаем транскрипцию для файла: {file_path}")

        # Если файл MP3, конвертируем его в WAV
        if file_path.endswith(('.mp3', '.ogg', '.flac')):
            wav_file_path = os.path.splitext(file_path)[0] + ".wav"
            convert_mp3_to_wav(file_path, wav_file_path)
            file_path = wav_file_path

        # Приводим WAV файл к корректному формату
        formatted_wav_path = os.path.splitext(file_path)[0] + "_formatted.wav"
        ensure_wav_format(file_path, formatted_wav_path)
        file_path = formatted_wav_path

        # Проверка файла после конвертации
        logging.info(f"После конвертации: {file_path}")

        # Инициализация модели и распознавания
        model = Model(VOSK_MODEL_PATH)
        recognizer = KaldiRecognizer(model, 16000)

        with wave.open(file_path, "rb") as wf:
            logging.info(f"Чтение файла {file_path}...")

            if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
                raise ValueError("Аудиофайл должен быть моно, с частотой дискретизации 16000 и 16-битной глубиной")

            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                logging.info(f"Обрабатываем блок данных... длина: {len(data)}")
                if recognizer.AcceptWaveform(data):
                    result = recognizer.Result()
                    logging.info(f"Результат распознавания: {result}")
                    if result:
                        result_json = json.loads(result)
                        logging.info(f"Транскрипция успешна: {result_json.get('text', '')}")
                        return result_json.get("text", "")
    except Exception as e:
        logging.error(f"Ошибка при транскрипции аудиофайла {file_path}: {e}")
        return "Не распозналось"
    finally:
        if formatted_wav_path and os.path.exists(formatted_wav_path):
            os.remove(formatted_wav_path)

    return "Не распозналось"




# def transcribe_audio(file_path: str) -> str:
#     formatted_wav_path = None  # Инициализируем переменную заранее
#     try:
#         """Транскрипция аудиофайла с использованием Vosk"""
#         # Если файл MP3, конвертируем его в WAV
#         if file_path.endswith(('.mp3', '.ogg', '.flac')):
#             wav_file_path = os.path.splitext(file_path)[0] + ".wav"
#             convert_mp3_to_wav(file_path, wav_file_path)
#             file_path = wav_file_path
#
#         # Приводим WAV файл к корректному формату
#         formatted_wav_path = os.path.splitext(file_path)[0] + "_formatted.wav"
#         ensure_wav_format(file_path, formatted_wav_path)
#         file_path = formatted_wav_path
#
#         # Инициализация модели и распознавания
#         model = Model(VOSK_MODEL_PATH)
#         recognizer = KaldiRecognizer(model, 16000)
#
#         with wave.open(file_path, "rb") as wf:
#             if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
#                 raise ValueError("Аудиофайл должен быть моно, с частотой дискретизации 16000 и 16-битной глубиной")
#
#             while True:
#                 data = wf.readframes(4000)
#                 if len(data) == 0:
#                     break
#                 if recognizer.AcceptWaveform(data):
#                     result = recognizer.Result()
#                     result_json = json.loads(result)
#                     return result_json.get("text", "")
#     except Exception as e:
#         logging.error(f"Ошибка при транскрипции аудиофайла {file_path}: {e}")
#         return "Не распозналось"  # Возвращаем строку по умолчанию, если что-то пошло не так
#     finally:
#         # Удаляем временный файл, если он был создан
#         if formatted_wav_path and os.path.exists(formatted_wav_path):
#             os.remove(formatted_wav_path)
#
#     return "Не распозналось"  # Если транскрипция не удалась
