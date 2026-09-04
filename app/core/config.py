import os
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not PINECONE_API_KEY:
    raise RuntimeError("PINECONE_API_KEY is not set")

if not PINECONE_INDEX:
    raise RuntimeError("PINECONE_INDEX is not set")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not set")