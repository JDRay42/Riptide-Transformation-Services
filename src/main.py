import os
import json
import httpx
from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import PlainTextResponse
from fastapi.exceptions import RequestValidationError
from decouple import config
from .ner_service import ner_router
from .text2vec_service import text2vec_router
from .paraphraser_service import paraphraser_router

SCHEME = config('SCHEME', default='https')
HOST = config('HOST', default='localhost')
PORT = config('PORT', default=8019, cast=int)

ENV = config('ENVIRONMENT', default='development')

verifySSL = True if ENV == 'production' else False

if ENV == 'development':
    API_KEY = config('DEV_API_KEY')
else:
    # Fetch production API key or handle it differently
    API_KEY = config('PROD_API_KEY')

app = FastAPI()

templates = Jinja2Templates(directory="web/templates")

base_directory = os.path.dirname(os.path.abspath(__file__))
static_directory = os.path.join(base_directory, "..", "web", "static")
app.mount("/static", StaticFiles(directory=static_directory), name="static")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
  print(exc)
  return PlainTextResponse(str(exc), status_code=400)

@app.exception_handler(Exception) 
async def general_exception_handler(request, exc):
  print(exc)
  return PlainTextResponse('Internal server error', status_code=500)
@app.get("/test")
def test_endpoint():
    return {"message": "Test endpoint is working"}

def verify_api_key(request: Request):
    expected_api_key = API_KEY
    provided_api_key = request.headers.get("X-API-KEY")

    if provided_api_key != expected_api_key:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return provided_api_key

@app.get("/styles.css")
async def read_css():
    with open("web/static/styles.css", "r") as f:
        content = f.read()
    return PlainTextResponse(content, media_type="text/css")

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})

@app.get("/nertags/")
def get_ner_tags(request: Request):
    return templates.TemplateResponse("nertags.html", {"request": request})

@app.get("/vectors/")
def get_vectors(request: Request):
    return templates.TemplateResponse("vectors.html", {"request": request})

@app.get("/paraphraser/")
def get_paraphrase_page(request: Request):
    return templates.TemplateResponse("paraphraser.html", {"request": request})

@app.post("/nertags/", response_model=None)
async def post_ner_tags(request: Request, text: str = Form(...)):

  headers = {
    "X-API-KEY": API_KEY  
  }

  url = f"{SCHEME}://{HOST}:{PORT}/ner/"
    
  async with httpx.AsyncClient(verify=verifySSL) as client:

    response = await client.post(url, json={"text": text}, headers=headers)

    # Check if the response was successful
    if response.status_code == 200:
        tags = response.json()["entities"]
    else:
        # Handle error response here. For now, let's just log the error.
        error_message = response.json()["error"]
        print(f"Error: {error_message}")
        return templates.TemplateResponse("error_template.html", {"request": request, "error_message": error_message})
    
    tags = response.json()["entities"]
    print (tags)
    parsed_tags = [eval(tag) for tag in tags]

    # Rendering the nertags.html template, passing the vector as context
    return templates.TemplateResponse("nertags.html", {"request": request, "tags": parsed_tags, "entered_text": text})
  
@app.post("/vectors/", response_model=None)
async def post_vectors(request: Request):
    # Extracting the text from the form submission
    form_data = await request.form()
    text = form_data.get("text")
    
    headers = {
        "X-API-KEY": API_KEY
    }
    
    # Forwarding the text to the text2vec service to obtain the vector
    async with httpx.AsyncClient(verify=verifySSL) as client:
        url = f"{SCHEME}://{HOST}:{PORT}/text2vec/"
        response = await client.post(url, json={"text": text}, headers=headers)
        
        # Check if the response was successful
        if response.status_code == 200:
            vector = response.json()["vector"]
        else:
            # Handle error response here.
            error_message = response.json()["error"]
            print(f"Error: {error_message}")
            return templates.TemplateResponse("error_template.html", {"request": request, "error_message": error_message})

    # Rendering the vectors.html template, passing the vector as context
    return templates.TemplateResponse("vectors.html", {"request": request, "vector": vector, "entered_text": text})
  
@app.post("/paraphraser/", response_model=None)
async def post_paraphraser(request: Request):
    form_data = await request.form()
    text = form_data.get("text")
    multipleResponses = form_data.get("multipleResponses") == "on"
    numResponses = int(form_data.get("numResponses", 1))
    
    headers = {
        "X-API-KEY": API_KEY
    }
    
    async with httpx.AsyncClient(verify=verifySSL) as client:

        # Determine the appropriate endpoint based on user's choice
        if multipleResponses:
            url = f"{SCHEME}://{HOST}:{PORT}/paraphrase/multi/"
            response = await client.post(url, json={"text": text, "return_sequences": numResponses}, headers=headers)
            # Check if the response was successful
            if response.status_code == 200:
                paraphrases = response.json()["paraphrases"]
            else:
                # Handle error response here.
                error_message = response.json()["error"]
                print(f"Error: {error_message}")
                return templates.TemplateResponse("error_template.html", {"request": request, "error_message": error_message})
        else:
            url = f"{SCHEME}://{HOST}:{PORT}/paraphrase/"
            response = await client.post(url, json={"text": text}, headers=headers)
            # Check if the response was successful
            if response.status_code == 200:
                paraphrases = [response.json()["paraphrased_text"]]
            else:
                # Handle error response here.
                error_message = response.json()["error"]
                print(f"Error: {error_message}")
                return templates.TemplateResponse("error_template.html", {"request": request, "error_message": error_message})

        # Rendering the paraphraser.html template, passing the vector as context
        return templates.TemplateResponse("paraphraser.html", {"request": request, "paraphrases": paraphrases, "entered_text": text})

# Including the routers with the API key verification
app.include_router(ner_router, prefix="/ner", dependencies=[Depends(verify_api_key)])
app.include_router(text2vec_router, prefix="/text2vec", dependencies=[Depends(verify_api_key)])
app.include_router(paraphraser_router, prefix="/paraphrase", dependencies=[Depends(verify_api_key)])
