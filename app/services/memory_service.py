from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.conversation import ConversationMessage


def save_message(
    patient_id: str,
    session_id: str,
    role: str,
    content: str,
):
    db: Session = SessionLocal()

    try:
        message = ConversationMessage(
            patient_id=patient_id,
            session_id=session_id,
            role=role,
            content=content,
        )

        db.add(message)
        db.commit()

    finally:
        db.close()


def get_conversation_history(
    patient_id: str,
    session_id: str,
    limit: int = 30,
):
    db: Session = SessionLocal()

    try:
        # Load recent memory for this patient across sessions so facts survive
        # refreshes and newly started conversations.
        messages = (
            db.query(ConversationMessage)
            .filter(
                ConversationMessage.patient_id == patient_id,
            )
            .order_by(
                ConversationMessage.created_at.desc(),
                ConversationMessage.id.desc(),
            )
            .limit(limit)
            .all()
        )

        # Oldest to newest for the LLM.
        messages.reverse()

        return [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in messages
        ]

    finally:
        db.close()
