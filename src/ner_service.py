import re
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from decouple import config
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

NER_TOKENIZER = config('NER_TOKENIZER', default="dbmdz/bert-large-cased-finetuned-conll03-english")
NER_MODEL = config('NER_MODEL', default="dbmdz/bert-large-cased-finetuned-conll03-english")
WORD_LIMIT = config('WORD_LIMIT', default=400, cast=int)

def merge_capitalized_sequences(text, entities):
    """
    Merges sequences of capitalized words in the text.
    
    Args:
    - text (str): Original input text.
    - entities (list): List of recognized entities.
    
    Returns:
    - list: List of merged entities.
    """

    # Find sequences of capitalized words
    capitalized_sequences = re.findall(r'\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\b', text)

    merged_entities = entities.copy()

    for sequence in capitalized_sequences:
        sequence_tokens = sequence.split()
        
        # If the sequence is just one word or is the start of the text, skip it
        if len(sequence_tokens) == 1 or text.startswith(sequence):
            continue

        # Find entities that match the start of the sequence
        matching_entities = [e for e in merged_entities if e['word'] == sequence_tokens[0]]

        # If the first word of the sequence is recognized as an entity
        if matching_entities:
            # Take the first matching entity (assuming it's the most relevant)
            entity = matching_entities[0]

            # Update the word in the entity to the full sequence
            entity_index = merged_entities.index(entity)
            merged_entities[entity_index]['word'] = sequence

            # Remove subsequent entities that are part of the sequence
            for token in sequence_tokens[1:]:
                token_entities = [e for e in merged_entities if e['word'] == token or e['word'] == "##" + token]
                for te in token_entities:
                    merged_entities.remove(te)

    return merged_entities

def merge_adjacent_entities(entities):
    """
    Merges adjacent entities based on the same entity type, token continuation, and '##s' pattern.
    
    Args:
    - entities (list): List of recognized entities.
    
    Returns:
    - list: List of merged entities.
    """
    if not entities:
        return []

    merged_entities = [entities[0]]

    for entity in entities[1:]:
        prev_entity = merged_entities[-1]
        
        # Merge entities if the current entity starts with "##"
        if entity['word'].startswith("##"):
            prev_entity['word'] += entity['word'].replace("##", "")
            prev_entity['score'] = (prev_entity['score'] + entity['score']) / 2  # average score
        # Merge entities of the same type
        elif entity['entity'] == prev_entity['entity']:
            prev_entity['word'] += " " + entity['word'].replace("##", "")
            prev_entity['score'] = (prev_entity['score'] + entity['score']) / 2  # average score
        else:
            merged_entities.append(entity)

    return merged_entities

# Create a router instance
ner_router = APIRouter()

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(NER_TOKENIZER)
model = AutoModelForTokenClassification.from_pretrained(NER_MODEL)

# Create NER pipeline
nlp_ner = pipeline("ner", model=model, tokenizer=tokenizer)

class NERRequest(BaseModel):
    text: str

class NERResponse(BaseModel):
    entities: list

@ner_router.post("/", response_model=NERResponse) 
async def named_entity_recognition(request: NERRequest):
    words = request.text.split()
    if len(words) > WORD_LIMIT:
        return JSONResponse(content={"error": f"Input text exceeds {WORD_LIMIT} words. Please provide shorter text."}, status_code=400)

    entities = nlp_ner(request.text)
    entities = merge_adjacent_entities(entities)
    entities = merge_capitalized_sequences(request.text, entities)

    # Convert numpy types to standard types and format as pretty strings
    formatted_entities = []
    for entity in entities:
        formatted_entity = f"{{'word': '{entity['word']}', 'score': {float(entity['score']):.4f}, 'entity': '{entity['entity']}'}}"
        formatted_entities.append(formatted_entity)

    return {"entities": formatted_entities}
