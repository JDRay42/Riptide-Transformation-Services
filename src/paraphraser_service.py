import os
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from transformers import T5ForConditionalGeneration, T5Tokenizer
from typing import Optional

# Reading environment variables or setting default values
PARAPHRASE_TEMPERATURE = float(os.environ.get("PARAPHRASE_TEMPERATURE", 0.9))
PARAPHRASE_MODEL_SIZE = os.environ.get("PARAPHRASE_MODEL_SIZE", "t5-small")
PARAPHRASE_TOP_P = float(os.environ.get("PARAPHRASE_TOP_P", 0.9))
PARAPHRASE_TOP_K = int(os.environ.get("PARAPHRASE_TOP_K", 35))
PARAPHRASE_REPETITION_PENALTY = float(os.environ.get("PARAPHRASE_REPETITION_PENALTY", 1.2))
WORD_LIMIT = int(os.environ.get("WORD_LIMIT", 400))

# Create a router instance
paraphraser_router = APIRouter()

# Define the request and response models
class ParaphraseRequest(BaseModel):
    text: str

class ParaphraseResponse(BaseModel):
    paraphrased_text: str

class ParaphraseMultipleRequest(BaseModel):
    text: str
    return_sequences: Optional[int] = 5
    
@paraphraser_router.post("/", response_model=ParaphraseResponse)
async def paraphrase_text(request: ParaphraseRequest):
    words = request.text.split()
    if len(words) > WORD_LIMIT:
        return JSONResponse(content={"error": f"Input text exceeds {WORD_LIMIT} words. Please provide shorter text."}, status_code=400)
    paraphrased_text = paraphrase(request.text)
    return {"paraphrased_text": paraphrased_text}

def paraphrase(text):
  tokenizer = T5Tokenizer.from_pretrained(PARAPHRASE_MODEL_SIZE)
  model = T5ForConditionalGeneration.from_pretrained(PARAPHRASE_MODEL_SIZE)
  input_ids = tokenizer.encode("paraphrase: " + text, return_tensors="pt")
  output = model.generate(input_ids, 
                        max_length=WORD_LIMIT, 
                        temperature=PARAPHRASE_TEMPERATURE, 
                        top_p=PARAPHRASE_TOP_P, 
                        top_k=PARAPHRASE_TOP_K, 
                        repetition_penalty=PARAPHRASE_REPETITION_PENALTY)
  paraphrased_text = tokenizer.decode(output[0], skip_special_tokens=True)
  return paraphrased_text

@paraphraser_router.post("/multi/")
def paraphrases(request: ParaphraseMultipleRequest):
  return {"paraphrases": paraphrases(request.text, 
                                     request.return_sequences)}

def paraphrases(text,
               return_sequences):
  tokenizer = T5Tokenizer.from_pretrained(PARAPHRASE_MODEL_SIZE)
  model = T5ForConditionalGeneration.from_pretrained(PARAPHRASE_MODEL_SIZE)
  input_ids = tokenizer.encode("paraphrase: " + text, return_tensors="pt") 
  outputs = model.generate(
      input_ids,
      do_sample=True, 
      max_length=WORD_LIMIT, 
      temperature=PARAPHRASE_TEMPERATURE, 
      top_p=PARAPHRASE_TOP_P, 
      top_k=PARAPHRASE_TOP_K, 
      repetition_penalty=PARAPHRASE_REPETITION_PENALTY,
      num_return_sequences=return_sequences
  )
  arrayOfParaphrases = []
  for output in outputs:
      paraphrrase = tokenizer.decode(output, skip_special_tokens=True)
      arrayOfParaphrases.append(paraphrrase)
  return arrayOfParaphrases