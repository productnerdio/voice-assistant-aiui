import base64
import json
import time
import logging

from fastapi import FastAPI, UploadFile, BackgroundTasks, Header
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from ai import get_completion
from stt import transcribe
from tts import to_speech

app = FastAPI()
logging.basicConfig(level=logging.INFO)

@app.post("/inference")
async def infer(audio: UploadFile, background_tasks: BackgroundTasks, conversation: str = Header(default=None)):
    logging.debug("Received request")
    start_time = time.time()

    # Step 1: Transcribe the audio
    user_prompt_text = await transcribe(audio)
    
    # Step 2: Generate and send an interim response immediately
    interim_response = "One moment, let me check that for you."
    interim_response_audio_filepath = await to_speech(interim_response, background_tasks)
    background_tasks.add_task(send_interim_response, interim_response_audio_filepath)
    
    
    # Step 3: Process AI completion
    ai_response_text = await get_completion(user_prompt_text, conversation)
    
    # Step 4: Convert AI response to speech
    ai_response_audio_filepath = await to_speech(ai_response_text, background_tasks)

    # Step 5: Log total processing time
    logging.info(f'Total processing time: {time.time() - start_time} seconds')
    
    # Step 6: Return the final audio file response
    return FileResponse(
        path=ai_response_audio_filepath, 
        media_type="audio/mpeg",
        headers={"text": _construct_response_header(user_prompt_text, ai_response_text)}
    )

@app.get("/")
async def root():
    return RedirectResponse(url="/index.html")

app.mount("/", StaticFiles(directory="/app/frontend/dist"), name="static")

def _construct_response_header(user_prompt, ai_response):
    """Encodes the conversation data into a base64 string for headers."""
    return base64.b64encode(
        json.dumps(
            [{"role": "user", "content": user_prompt}, {"role": "assistant", "content": ai_response}]
        ).encode('utf-8')
    ).decode("utf-8")

async def send_interim_response(interim_response_audio_filepath):
    # This function could, for example, send the interim response file over WebSocket or another channel
    # The specifics of this function will depend on your client-side handling
    pass
