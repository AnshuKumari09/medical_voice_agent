from groq import AsyncGroq

from app.core.config import GROQ_API_KEY
from app.services.pinecone_service import search_medical_knowledge
from app.services.memory_service import (
    get_conversation_history,
    save_message,
)


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
        "temperature",
        "dehydration",
        "dizziness",
        "nausea",
        "allergy",
        "injury",
        "wound",
    ]

    message_lower = message.lower()

    return any(
        keyword in message_lower
        for keyword in medical_keywords
    )


async def generate_response(
    patient_id: str,
    session_id: str,
    message: str,
) -> str:

    # =======================================
    # Conversation Memory
    # =======================================

    history = get_conversation_history(
        patient_id=patient_id,
        session_id=session_id,
        limit=30,
    )

    print("Conversation history:", history)

    # =======================================
    # Medical Knowledge Retrieval
    # =======================================

    context = ""

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

    # =======================================
    # System Prompt
    # =======================================

    system_prompt = """
You are MediReach, a friendly medical AI voice assistant.

Your job is to have a natural and helpful conversation with the patient.

IMPORTANT RULES:

- Return ONLY the final response to the patient.
- NEVER output thinking or reasoning.
- NEVER output <think> or </think>.
- NEVER explain your internal reasoning.
- NEVER mention Pinecone, RAG, embeddings, retrieval, context, or internal systems.
- Keep responses short and conversational.
- Usually respond in 1-3 sentences.
- Ask only 1-2 relevant questions when more information is needed.
- Use previous conversation messages as memory for this patient, including messages from earlier sessions.
- If the patient asks about information they already gave you, answer from the conversation memory instead of starting over.
- Do not give a definitive diagnosis.
- Do not claim certainty about a medical condition.
- Provide general health information.
- If symptoms sound serious or potentially life-threatening, advise the patient to seek immediate medical attention.
- If appropriate, recommend consulting a qualified doctor.
- Do not unnecessarily scare the patient.
- Speak naturally because your response may be converted into speech.

LANGUAGE:

- Respond in the same language as the patient.
- If the patient speaks Hindi, respond in Hindi.
- If the patient speaks Hinglish, respond naturally in Hinglish.
- If the patient speaks English, respond in English.

MEDICAL KNOWLEDGE:

Use the provided medical knowledge when it is relevant to the patient's question.

{context}
"""

    prompt = system_prompt.format(
        context=(
            context
            if context
            else "No medical knowledge retrieval was needed for this message."
        )
    )

    # =======================================
    # Build Messages
    # =======================================

    messages = [
        {
            "role": "system",
            "content": prompt,
        }
    ]

    # Previous conversation
    messages.extend(history)

    # Current user message
    messages.append(
        {
            "role": "user",
            "content": message,
        }
    )

    # =======================================
    # LLM
    # =======================================

    completion = await client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.5,
        max_tokens=150,
        reasoning_effort="none",
    )

    # =======================================
    # Extract Response
    # =======================================

    response = completion.choices[0].message.content.strip()

    # =======================================
    # Safety cleanup
    # =======================================

    if "<think>" in response:

        response = response.split(
            "<think>",
            1
        )[0].strip()

    if "</think>" in response:

        response = response.split(
            "</think>",
            1
        )[-1].strip()

    # =======================================
    # Save Conversation
    # =======================================

    save_message(
        patient_id=patient_id,
        session_id=session_id,
        role="user",
        content=message,
    )

    save_message(
        patient_id=patient_id,
        session_id=session_id,
        role="assistant",
        content=response,
    )

    print("Conversation saved to Supabase")

    return response
