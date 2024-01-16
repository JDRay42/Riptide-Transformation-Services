import requests


class NERService:
    def __init__(self):
        self.endpoint = "http://localhost:5005/model/parse"

    def get_entities(self, text):
        response = requests.post(self.endpoint, json={"text": text})
        data = response.json()
        entities = [
            {"word": e["text"], "score": e["confidence_entity"], "entity": e["entity"]}
            for e in data["entities"]
        ]
        return {"entities": entities}


def merge_consecutive_entities(entities):
    merged_entities = []
    prev_entity = None
    for entity in entities:
        if (
            prev_entity
            and prev_entity["entity"] == entity["entity"]
            and entity["score"] > 0.5
        ):
            prev_entity["word"] += f" {entity['word']}"
            prev_entity["score"] = (prev_entity["score"] + entity["score"]) / 2
        else:
            if prev_entity:
                merged_entities.append(prev_entity)
            prev_entity = entity.copy()
    if prev_entity:
        merged_entities.append(prev_entity)
    return merged_entities


def merge_based_on_capitalization(text, entities):
    words = text.split()
    current_entity_index = 0
    merged_entities = []

    for i in range(len(words)):
        if (
            current_entity_index < len(entities)
            and words[i] == entities[current_entity_index]["word"].split()[0]
        ):
            entity_words = entities[current_entity_index]["word"].split()
            end_index = i + len(entity_words) - 1

            # If next word is capitalized and not part of the current entity, extend the current entity
            if (
                end_index + 1 < len(words)
                and words[end_index + 1][0].isupper()
                and (
                    current_entity_index == len(entities) - 1
                    or words[end_index + 1]
                    != entities[current_entity_index + 1]["word"].split()[0]
                )
            ):
                entity_words.append(words[end_index + 1])
                end_index += 1

            merged_entities.append(
                {
                    "word": " ".join(entity_words),
                    "score": entities[current_entity_index]["score"],
                    "entity": entities[current_entity_index]["entity"],
                }
            )
            current_entity_index += 1
        elif words[i][0].isupper():
            merged_entities.append(
                {
                    "word": words[i],
                    "score": 0.5,  # arbitrary score
                    "entity": "I-MISC",  # default to miscellaneous entity
                }
            )

    return merged_entities


def merge_names_with_initials(entities):
    """
    Merges entities that appear to be names with initials, e.g., "J.", "K.", "Rowling" -> "J. K. Rowling"
    """
    merged_entities = []
    skip_next = False

    for i in range(len(entities)):
        if skip_next:
            skip_next = False
            continue
        
        entity = entities[i]
        
        # If the entity is a single initial and not the last entity
        if len(entity['word']) == 2 and entity['word'][1] == '.' and i != len(entities) - 1:
            next_entity = entities[i+1]

            # If the next entity is also an initial, merge both initials and look further
            if len(next_entity['word']) == 2 and next_entity['word'][1] == '.':
                merged_word = entity['word'] + " " + next_entity['word']
                current_score = (entity['score'] + next_entity['score']) / 2
                i += 1
                skip_next = True

                # Keep looking for more parts of the name
                while i+1 < len(entities) and len(entities[i+1]['word']) > 2 and entities[i+1]['word'][0].isupper():
                    i += 1
                    merged_word += " " + entities[i]['word']
                    current_score = (current_score + entities[i]['score']) / 2
                    skip_next = True

            # If the next entity is a regular name part, just merge the initial with it
            else:
                merged_word = entity['word'] + " " + next_entity['word']
                current_score = (entity['score'] + next_entity['score']) / 2
                skip_next = True

            merged_entities.append({"word": merged_word, "score": current_score, "entity": entity['entity']})

        else:
            merged_entities.append(entity)

    return merged_entities

def refine_merged_entities(merged_entities, expected_entities):
    refined_entities = []

    for entity in merged_entities:
        word = entity["word"]
        score = entity["score"]
        ent_type = entity["entity"]

        # Add the entity if it's in the expected list
        if word in expected_entities:
            refined_entities.append({"word": word, "score": score, "entity": ent_type})

    return refined_entities


# Sample usage
ner_service = NERService()
