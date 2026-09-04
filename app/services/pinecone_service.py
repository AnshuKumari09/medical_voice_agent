from pinecone import Pinecone

from app.core.config import (
    PINECONE_API_KEY,
    PINECONE_INDEX,
)


# Pinecone client
pc = Pinecone(
    api_key=PINECONE_API_KEY
)

# Existing Pinecone index
pinecone_index = pc.Index(
    PINECONE_INDEX
)


def search_medical_knowledge(
    query_text: str,
    top_k: int = 5
):
    # Create embedding for the USER QUERY only
    query_embedding = pc.inference.embed(
        model="multilingual-e5-large",
        inputs=[query_text],
        parameters={
            "input_type": "query"
        }
    )

    # Search existing vectors
    results = pinecone_index.query(
        vector=query_embedding[0]["values"],
        top_k=top_k,
        include_metadata=True
    )

    matches = []

    for match in results["matches"]:
        metadata = match.get("metadata", {})

        matches.append({
            "score": match.get("score"),
            "text": metadata.get("text", ""),
            "metadata": metadata
        })

    return matches