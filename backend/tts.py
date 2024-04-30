import logging
import os
import time
import uuid
import requests
from fastapi import BackgroundTasks
from gtts import gTTS
import edge_tts
from util import delete_file

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

LANGUAGE = os.getenv("LANGUAGE", "en")
TTS_PROVIDER = os.getenv("TTS_PROVIDER", "EDGETTS")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", None)
ELEVENLABS_VOICE = os.getenv("ELEVENLABS_VOICE", "EXAVITQu4vr4xnSDxMaL")
EDGETTS_VOICE = os.getenv("EDGETTS_VOICE", "en-US-EricNeural")


async def to_speech(text, background_tasks: BackgroundTasks):
    if TTS_PROVIDER == "gTTS":
        return _gtts_to_speech(text, background_tasks)
    elif TTS_PROVIDER == "ELEVENLABS":
        return await _elevenlabs_to_speech_streaming(text, background_tasks)
    elif TTS_PROVIDER == "STREAMELEMENTS":
        return _streamelements_to_speech(text, background_tasks)
    elif TTS_PROVIDER == "EDGETTS":
        return await _edge_tts_to_speech(text, background_tasks)
    else:
        raise ValueError(f"env var TTS_PROVIDER set to unsupported value: {TTS_PROVIDER}")

async def _elevenlabs_to_speech_streaming(text, background_tasks: BackgroundTasks):
    start_time = time.time()
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE}/stream"
    payload = {
        "text": text,
        "model_id": "eleven_turbo_v2",  # Adjust this as necessary
        "optimize_streaming_latency": 1  # Enable normal latency optimizations
    }
    headers = {
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }

    response = requests.post(url, json=payload, headers=headers, stream=True)

    filepath = f"/tmp/{uuid.uuid4()}.mp3"
    if response.status_code == 200:
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        background_tasks.add_task(delete_file, filepath)
        logging.info('Streaming TTS time: %s seconds', time.time() - start_time)
        return filepath
    else:
        logging.error('Failed to stream TTS: %s', response.text)
        raise Exception("Failed to stream TTS")

def _gtts_to_speech(text, background_tasks: BackgroundTasks):
    start_time = time.time()
    tts = gTTS(text, lang=LANGUAGE)
    filepath = f"/tmp/{uuid.uuid4()}.mp3"
    tts.save(filepath)
    background_tasks.add_task(delete_file, filepath)
    logging.info('TTS time: %s seconds', time.time() - start_time)
    return filepath

def _streamelements_to_speech(text, background_tasks: BackgroundTasks):
    start_time = time.time()
    response = requests.get(f"https://api.streamelements.com/kappa/v2/speech?voice=Salli&text={text}")
    filepath = f"/tmp/{uuid.uuid4()}.mp3"
    with open(filepath, "wb") as f:
        f.write(response.content)
    background_tasks.add_task(delete_file, filepath)
    logging.info('TTS time: %s seconds', time.time() - start_time)
    return filepath

async def _edge_tts_to_speech(text, background_tasks: BackgroundTasks):
    start_time = time.time()
    communicate = edge_tts.Communicate(text, EDGETTS_VOICE)
    filepath = f"/tmp/{uuid.uuid4()}.mp3"
    await communicate.save(filepath)
    background_tasks.add_task(delete_file, filepath)
    logging.info('TTS time: %s seconds', time.time() - start_time)
    return filepath
