from groq import AsyncGroq

from app.core.config import GROQ_API_KEY
from app.services.pinecone_service import search_medical_knowledge
from app.services.tts_service import speak_text
import asyncio
from app.services.tts_service import speak_text
client = AsyncGroq(
    api_key=GROQ_API_KEY
)


MODEL = "qwen/qwen3.6-27b"


def is_medical_question(message: str) -> bool:

    medical_keywords = [
        "symptom",
        "pain",
        "fever",
        "cough",
        "cold",
        "headache",
        "medicine",
        "medication",
        "tablet",
        "disease",
        "diagnosis",
        "treatment",
        "doctor",
        "blood",
        "pressure",
        "sugar",
        "diabetes",
        "vomiting",
        "diarrhea",
        "pregnancy",
        "infection",
        "rash",
        "breathing",
        "chest",
        "health",
        "temperature"
    ]

    message_lower = message.lower()

    return any(
        keyword in message_lower
        for keyword in medical_keywords
    )


async def generate_response(
    patient_id: str,
    message: str
) -> str:

    context = ""

    # Only search Pinecone when the message is medical
    if is_medical_question(message):

        results = search_medical_knowledge(
            query_text=message,
            top_k=5
        )

        context = "\n\n".join(
            result["text"]
            for result in results
            if result.get("text")
        )

    
    system_prompt = """
    You are MediReach, a friendly medical AI voice assistant.

    Your job is to have a natural, short conversation with the patient.

    IMPORTANT:
    - Return ONLY the final response to the patient.
    - NEVER output thinking, reasoning, analysis, drafts, or internal steps.
    - NEVER output <think> or </think>.
    - Do not explain how you generated the answer.
    - Do not mention Pinecone, embeddings, RAG, context, or internal systems.
    - Keep responses short because they will be spoken aloud.
    - Ask only 1 or 2 relevant follow-up questions when necessary.
    - For casual messages, respond casually.
    - For medical questions, use the provided medical knowledge.
    - Do not give a definitive diagnosis.
    - If symptoms sound serious, advise the patient to seek medical attention.

    Medical knowledge:
    {context}
    """

    prompt = system_prompt.format(
        context=context if context else "No medical knowledge retrieval needed."
    )

    completion = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": message
            }
        ],
        temperature=0.5,
        max_tokens=150,
        reasoning_effort="none"
    )


    response = completion.choices[0].message.content.strip()

    # Remove thinking if it somehow appears
    if "<think>" in response:
        response = response.split("<think>", 1)[0].strip()

    if "</think>" in response:
        response = response.split("</think>", 1)[-1].strip()

    # Speak without blocking FastAPI event loop
    await asyncio.to_thread(speak_text, response)

    return response