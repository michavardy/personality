from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
import markdown
from bs4 import BeautifulSoup
#from langchain import LangChain
from pathlib import Path

app = FastAPI()

class PromptRequest(BaseModel):
    action: str
    prompt: str

def parse_soup(soup) -> dict:
    parsed = {}
    current_section = None

    for element in soup:
        if element.name == 'h1':
            current_section = element.get_text()
            parsed[current_section] = []
        elif element.name == 'p' and current_section:
            parsed[current_section].append(element.get_text())
        elif element.name == 'ul' and current_section:
            for li in element.find_all('li'):
                parsed[current_section].append(li.get_text())
    return parsed

def md_to_dict(md:str)-> dict:
    html = markdown.markdown(md)
    soup = BeautifulSoup(html, 'html.parser')
    return parse_soup(soup)

rules = md_to_dict(Path('scenarios/rules.md').read_text())
breakpoint()
RULES = [
    "You can describe certain parts of your surroundings.",
    "You can address a group or specific characters by direction or name.",
    "You have 10 minutes to solve the problem presented in the scenario."
]

SCENARIO = "You find yourself in a dark forest. The goal is to find the hidden treasure within 10 minutes."

CHARACTERS = [
    "character1",
    "character2",
    "character3"
]

# Initialize LangChain
lc = LangChain()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/rules")
async def get_rules():
    return {"rules": RULES}

@app.get("/scenario")
async def get_scenario():
    return {"scenario": SCENARIO}

@app.get("/characters")
async def get_characters():
    return {"characters": CHARACTERS}

@app.post("/handle_prompt")
async def handle_prompt(request: PromptRequest):
    if request.action not in ["describe", "go", "talk"] + CHARACTERS:
        raise HTTPException(status_code=400, detail="Invalid action.")
    
    # For now, we simply send the prompt to LangChain
    response = lc.generate_text(request.prompt)
    return {"response": response}

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred."},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
