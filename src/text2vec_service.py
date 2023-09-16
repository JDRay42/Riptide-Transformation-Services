'''
This transformation service is designed to align with the Weaviate configuration for Riptide Vectorizer.
If using Vectorizer and that configuration changes, this service will need to be updated accordingly.
'''

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from decouple import config

TEXT2VEC_MODEL = config('TEXT2VEC_MODEL', default="sentence-transformers/multi-qa-MiniLM-L6-cos-v1")
WORD_LIMIT = config('WORD_LIMIT', default=400, cast=int)

# Load the sentence transformer model
model_name = TEXT2VEC_MODEL
model = SentenceTransformer(model_name)

# Create a router instance
text2vec_router = APIRouter()

# Models for your request and response
class TextVectorRequest(BaseModel):
    text: str

class TextVectorResponse(BaseModel):
    vector: list

@text2vec_router.post("/", response_model=TextVectorResponse)
async def vectorize_text(request: TextVectorRequest):
    words = request.text.split()
    if len(words) > WORD_LIMIT:
        return JSONResponse(content={"error": f"Input text exceeds {WORD_LIMIT} words. Please provide shorter text."}, status_code=400)
    text = request.text
    vector = vectorize(text)
    return {"vector": vector}

def vectorize(text: str):
    # Get the embeddings using the sentence transformer model
    vector = model.encode([text])[0].tolist()
    return vector
