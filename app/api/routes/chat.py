from fastapi import (
    APIRouter,
    HTTPException,
    UploadFile,
    File,
    Form,
)

from app.models.chat import ChatRequest
from app.services.llm_service import generate_response
from app.services.stt_service import transcribe_audio
from app.services.tts_service import text_to_speech


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

        # 1. Speech → Text
        transcript = await transcribe_audio(file)

        print("🎤 Transcript:", transcript)


        # 2. Text → LLM
        response = await generate_response(
            patient_id=patient_id,
            message=transcript,
        )

        print("🤖 AI Response:", response)


        # 3. LLM Response → Speech
        audio_base64 = await text_to_speech(response)

        print("🔊 TTS generated successfully")


        # 4. Return JSON
        return {
            "transcript": transcript,
            "response": response,
            "audio": audio_base64,
        }

    except Exception as e:

        print("❌ Voice error:", e)

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
