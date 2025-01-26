from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from scrapper import chat,web_database

app = FastAPI(
    docs_url="/",
    title="Chatbot API",
    description="A simple chatbot API",
    version="0.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/scrape")
def scrape_data(email:str,link:str):
    try:
        web_database(email,link)
        return JSONResponse({"success": True})
    except Exception as e:
        return JSONResponse({"error" : f"{e}","success": False})

@app.get("/ask")
def handle_question(email:str,question:str):
    response = chat(email,question)
    return JSONResponse(content={"response": response})

