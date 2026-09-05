from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from app.models.chat import ChatRequest
from app.services.llm_service import generate_response
from app.services.stt_service import transcribe_audio
from app.services.tts_service import text_to_speech


router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)


@router.post("/")
async def chat(request: ChatRequest):
    try:
        response = await generate_response(
            patient_id=request.patient_id,
            session_id=request.session_id,
            message=request.message,
        )

        return {
            "response": response,
        }

    except Exception as e:
        print("Chat error:", e)

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.post("/voice")
async def voice_chat(
    patient_id: str = Form(...),
    session_id: str = Form(...),
    file: UploadFile = File(...),
):
    try:
        # 1. Speech to text
        transcript = await transcribe_audio(file)

        print("Transcript:", transcript)

        # 2. Text to AI response
        response = await generate_response(
            patient_id=patient_id,
            session_id=session_id,
            message=transcript,
        )

        print("AI Response:", response)

        # 3. AI response to speech
        audio_base64 = await text_to_speech(response)

        print("TTS generated successfully")

        return {
            "transcript": transcript,
            "response": response,
            "audio": audio_base64,
            "audio_type": "audio/mpeg",
        }

    except Exception as e:
        print("Voice error:", e)

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
