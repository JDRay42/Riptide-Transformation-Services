from fastapi.testclient import TestClient
from src.main import app
from decouple import config

WORD_LIMIT = int(config("WORD_LIMIT", default=400))

client = TestClient(app)

# Sample payload
sample_payload = {
    "text": """
Jenny Cox washed the dishes from the morning rush.  A few people idled in the dining room, 
but they’d cleared their tables and everything was queued up for her.  This far down, everyone 
knew what work was like, and no one wanted to make more work for anyone else.  She had heard it 
was different in the Mids, where people thought themselves fancy because they had some uppity 
management job or worked in IT and figured other people were there to serve them.  She found that 
kind of funny, because she’d also heard that people in the Up Top, where they had real power, were 
polite to the service staff and picked up after themselves, even though they didn’t make big messes.  
She didn’t know why people were the way they were, but found it interesting that it was the people 
in the middle of the giant sandwich that was the Silo that acted the worst, while the people above 
and below treated people well.  Her husband had thought the people at the top and bottom knew their 
places and were comfortable in them, while the people in the middle felt like they wanted to move up 
while fearing they’d get pushed down.  He spent a lot of time thinking about things, then telling her 
how he thought they were, which was one of the many things that led to her leaving him.
"""
}

words_in_sample = len(sample_payload["text"].split())
repetitions_needed = (WORD_LIMIT // words_in_sample) + 2  # +2 to ensure we exceed the limit
overloaded_payload = {"text": sample_payload["text"] * repetitions_needed}

def test_test_endpoint():
    response = client.get("/test")
    assert response.status_code == 200
    assert response.json() == {"message": "Test endpoint is working"}

def test_read_css():
    response = client.get("/styles.css")
    assert response.status_code == 200
    # You can add more checks related to the content of the CSS here.

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200

def test_get_ner_tags():
    response = client.get("/nertags/")
    assert response.status_code == 200

def test_get_vectors():
    response = client.get("/vectors/")
    assert response.status_code == 200

def test_get_paraphrase_page():
    response = client.get("/paraphraser/")
    assert response.status_code == 200

def test_post_ner_tags():
    response = client.post("/nertags/", data=sample_payload)
    assert response.status_code == 200

def test_post_vectors():
    response = client.post("/vectors/", data=sample_payload)
    assert response.status_code == 200

def test_post_paraphraser():
    response = client.post("/paraphraser/", data={**sample_payload, "multipleResponses": "on", "numResponses": "1"})
    assert response.status_code == 200

def test_post_ner_tags_overload():
    response = client.post("/nertags/", data=overloaded_payload)
    assert response.status_code == 200
    assert "Input text exceeds 400 words. Please provide shorter text." in response.text

def test_post_vectors_overload():
    response = client.post("/vectors/", data=overloaded_payload)
    assert response.status_code == 200
    assert "Input text exceeds 400 words. Please provide shorter text." in response.text
    
def test_post_paraphraser_overload():
    response = client.post("/paraphraser/", data=overloaded_payload)
    assert response.status_code == 200
    assert "Input text exceeds 400 words. Please provide shorter text." in response.text