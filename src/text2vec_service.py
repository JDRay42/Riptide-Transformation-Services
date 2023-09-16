"""
text2vec_service.py
===================

This service module offers functionalities to convert text into vectors using transformer models. 
It is designed to align with the Weaviate configuration for the Riptide Vectorizer. 
If using Riptide Vectorizer, any changes in the Vectorizer configuration necessitate updates to this service.

Imports:
    - Essential modules for API routing, request-response modeling, text vectorization, and configuration management.

Configuration:
    - TEXT2VEC_MODEL: Specifies the transformer model used for text-to-vector conversion.
    - WORD_LIMIT: Specifies the limit for the number of words in the vectorization input (default is 400).

Model Loading:
    - The Sentence Transformer model, as specified in the `TEXT2VEC_MODEL` configuration, is loaded.

Router:
    - An instance of the FastAPI APIRouter is created to manage routes specific to this service.

Models:
    - TextVectorRequest: Represents the structure of an input request for vectorization.
    - TextVectorResponse: Represents the structure of the output vector.

API Endpoints:
    - POST `/`: Converts the provided text in the `TextVectorRequest` to a vector and returns it as a `TextVectorResponse`.

"""


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
