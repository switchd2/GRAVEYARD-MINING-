import os

# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

# pyrefly: ignore [missing-import]
from openai import AsyncOpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

def get_openai_client() -> AsyncOpenAI | None:
    if OPENAI_API_KEY and not OPENAI_API_KEY.startswith("your_"):
        return AsyncOpenAI(api_key=OPENAI_API_KEY)
    return None

async def generate_embedding(text: str) -> list[float]:
    """
    Generates text embedding vector using OpenAI text-embedding-3-small (1536 dims).
    Falls back to simple hash-based pseudo-vector if API call fails or key is missing.
    """
    client = get_openai_client()
    if client:
        try:
            response = await client.embeddings.create(
                model="text-embedding-3-small",
                input=text.replace("\n", " ")
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating OpenAI embedding: {e}")

    # Fallback deterministic pseudo-vector generator (128 dims)
    import hashlib
    vec = []
    for i in range(128):
        h = hashlib.md5(f"{text}_{i}".encode()).hexdigest()
        val = (int(h[:4], 16) / 65535.0) * 2.0 - 1.0
        vec.append(round(val, 4))
    return vec
