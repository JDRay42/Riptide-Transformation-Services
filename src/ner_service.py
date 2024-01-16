"""
ner_service.py
==============

This module provides functionalities related to Named Entity Recognition (NER) using transformer models.

Imports:
    - Essential modules for string manipulation, routing, response formatting, and configuration management.
    - Components from the `transformers` library for tokenization, model loading, and NER pipelines.

Configuration:
    - NER_TOKENIZER: Tokenizer configuration for the NER model (default is "dbmdz/bert-large-cased-finetuned-conll03-english").
    - NER_MODEL: Model configuration for NER (default is "dbmdz/bert-large-cased-finetuned-conll03-english").
    - WORD_LIMIT: Limit for the number of words in the NER input (default is 400).

Functions:
    - `merge_capitalized_sequences`: Merges sequences of capitalized words in the text. Useful for handling entities that span multiple tokens.

API Endpoints:
    (Further details about the API endpoints provided by this service module should be documented here.)

"""

import re
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from decouple import config
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

NER_TOKENIZER = config('NER_TOKENIZER', default="dbmdz/bert-large-cased-finetuned-conll03-english")
NER_MODEL = config('NER_MODEL', default="dbmdz/bert-large-cased-finetuned-conll03-english")
WORD_LIMIT = config('WORD_LIMIT', default=400, cast=int)

import re

def merge_adjacent_entities(entities):
    """
    Merges adjacent entities based on the same entity type, token continuation, and '##s' pattern.
    Avoids merging distinct person names into a single entity.
    
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
        # Merge entities of the same type but avoid merging distinct person names
        elif entity['entity'] == prev_entity['entity'] and entity['entity'] != "I-PER":
            prev_entity['word'] += " " + entity['word'].replace("##", "")
            prev_entity['score'] = (prev_entity['score'] + entity['score']) / 2  # average score
        else:
            merged_entities.append(entity)

    return merged_entities

def merge_capitalized_sequences(text, entities):
    """
    Merges sequences of capitalized words in the text that are likely part of the same entity.
    
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
            
            # Only merge if the subsequent token in the sequence is the next word in the entity list
            next_entity_index = merged_entities.index(entity) + 1
            if next_entity_index < len(merged_entities) and merged_entities[next_entity_index]['word'] == sequence_tokens[1]:
                # Update the word in the entity to the full sequence
                entity_index = merged_entities.index(entity)
                merged_entities[entity_index]['word'] = sequence

                # Remove subsequent entities that are part of the sequence
                for token in sequence_tokens[1:]:
                    token_entities = [e for e in merged_entities if e['word'] == token or e['word'] == "##" + token]
                    for te in token_entities:
                        merged_entities.remove(te)

    return merged_entities

def split_text_into_chunks(text, word_limit):
    """
    Split the text into chunks that are within the word limit.
    """
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        if len(current_chunk) + 1 <= word_limit:
            current_chunk.append(word)
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

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
        chunks = split_text_into_chunks(request.text, WORD_LIMIT)
        entities = []
        
        for chunk in chunks:
            chunk_entities = nlp_ner(chunk)
            entities.extend(chunk_entities)
    else:
        entities = nlp_ner(request.text)

    entities = merge_adjacent_entities(entities)
    entities = merge_capitalized_sequences(request.text, entities)

    formatted_entities = []
    for entity in entities:
        formatted_entity = f"{{'word': '{entity['word']}', 'score': {float(entity['score']):.4f}, 'entity': '{entity['entity']}'}}"
        formatted_entities.append(formatted_entity)

    return {"entities": formatted_entities}
