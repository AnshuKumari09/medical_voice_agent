from fastapi import (
    APIRouter,
    HTTPException,
    UploadFile,
    File,
    Form,
)

from fastapi.responses import FileResponse

from app.models.chat import ChatRequest
from app.services.llm_service import generate_response
from app.services.stt_service import transcribe_audio
from app.services.tts_service import text_to_speech

import os


router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)


# ---------------------------------------
# Text Chat
# ---------------------------------------

@router.post("/")
async def chat(request: ChatRequest):

    try:

        response = await generate_response(
            patient_id=request.patient_id,
            message=request.message,
        )

        return {
            "response": response,
        }

    except Exception as e:

        print("❌ Chat error:", e)

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ---------------------------------------
# Voice Chat
# ---------------------------------------

@router.post("/voice")
async def voice_chat(
    patient_id: str = Form(...),
    file: UploadFile = File(...),
):

    try:

        # STT
        transcript = await transcribe_audio(file)

        print("🎤 Transcript:", transcript)

        # LLM
        response = await generate_response(
            patient_id=patient_id,
            message=transcript,
        )

        print("🤖 AI Response:", response)

        # TTS
        audio_path = await text_to_speech(response)

        print("🔊 TTS generated successfully")

        # Return JSON
        return {
            "transcript": transcript,
            "response": response,
            "audio_file": audio_path,
        }

    except Exception as e:

        print("❌ Voice error:", e)

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ---------------------------------------
# Voice Audio
# ---------------------------------------

@router.post("/voice/audio")
async def voice_chat_audio(
    patient_id: str = Form(...),
    file: UploadFile = File(...),
):

    audio_path = None

    try:

        # 1. STT
        transcript = await transcribe_audio(file)

        print("🎤 Transcript:", transcript)

        # 2. LLM
        response = await generate_response(
            patient_id=patient_id,
            message=transcript,
        )

        print("🤖 AI Response:", response)

        # 3. TTS
        audio_path = await text_to_speech(response)

        print("🔊 TTS generated successfully")
        print("🎵 Audio file:", audio_path)

        # 4. Return actual MP3
        return FileResponse(
            path=audio_path,
            media_type="audio/mpeg",
            filename="medireach_response.mp3",
            headers={
                "Content-Disposition": "inline; filename=medireach_response.mp3",
                "X-Transcript": transcript.replace("\n", " ").strip(),
                "X-Response": response.replace("\n", " ").strip(),
            },
        )

    except Exception as e:

        print("❌ Voice audio error:", e)

        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
