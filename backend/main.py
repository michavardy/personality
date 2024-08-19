import logging
import re
from typing import Dict
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .rag_prompt import create_prompt, chain
from .character_agents import get_response
from .objects import Prompt
from pathlib import Path
from .logging_config import setup_logging
from fastapi.templating import Jinja2Templates
from fastapi import Request
from .trigger_prompt_bank import trigger_prompt_list
from .rag_prompt import get_vector_store_dict
from .logging_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)
app = FastAPI()
vector_store_dict = get_vector_store_dict(from_file=True)
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
colors = [
    "Maroon",
    "Orange",
    "Purple",
    "Green",
    "Cyan",
    "Magenta",
    "Black",
    "Gray",
    "Maroon",
    "Navy",
    "Olive",
    "Teal",
    "Lime",
    "Silver",
    "Aqua",
    "Fuchsia",
    "Brown",
    "Yellow",
]


@app.get("/characters_color_map")
async def get_characterss_color_map():
    characters = [character.stem.lower() for character in Path('scenarios/stuck_in_elevator/characters').iterdir() if character.stem != "mc"]
    select_colors = colors[:len(characters)]
    character_color_map = {**{"user":"blue","all":"red"}, **{character:select_colors[index].lower() for index, character in enumerate(characters)}}
    return {"characters_color_map":character_color_map}

@app.get("/initial_prompt")
async def get_initial_prompt() -> dict[str, list[Prompt]]:
    initial_prompt_history = [prompt for prompt in trigger_prompt_list if prompt.trigger_type == "initial"]
    return {"response": initial_prompt_history}

@app.post("/trigger_prompt")
async def trigger_prompt(prompt_history: list[Prompt]) -> dict[str, list[Prompt]]:
    # prompt: initialPrompt.prompt, source:initialPrompt.source, destination: initialPrompt.destination, response:""
    response = await get_response(prompt_history)
    return {"response":response}

@app.post("/handle_prompt")
async def handle_prompt(prompt_history: list[Prompt]) -> dict[str, list[Prompt]]:
    try:
        if prompt_history[-1].trigger_type == "trigger":
            breakpoint()
        response = await get_response(prompt_history, vector_store_dict)
        return {"response":response}
    except Exception as e:
        print(f"Error handling prompt: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# Serve static files from /frontend/dist
#app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    print("Starting Uvicorn server")
    uvicorn.run(app, host="0.0.0.0", port=80)
