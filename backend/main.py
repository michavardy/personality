import logging
import re
import random
from functools import wraps
from typing import Dict, Callable
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .rag_prompt import create_prompt, chain
from .character_agents import get_response
from .objects import Prompt, Credentials, UserData
from .models import DBClient
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
client = DBClient()
vector_store_dict = get_vector_store_dict(from_file=False)
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
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

def thread_id(func: Callable):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        thread_id = request.headers.get("thread_id")
        if not thread_id:
            raise HTTPException(status_code=401, detail="Missing thread_id in headers")
        return await func(request, *args, **kwargs)
    return wrapper

@app.get('/test')
async def test():
    return "successful"

@app.post(f"/sign_in")
async def sign_in(response: Response, credentials:Credentials) -> bool:
    is_authenticated = client.authenticate(username=credentials.username, password=credentials.password)
    if not is_authenticated:
        return False
    user_id =client.get_user_id_by_username(username=credentials.username)
    thread_id = client.generate_thread_id()
    response.headers["thread_id"] = str(thread_id)
    response.headers["user_id"] = str(user_id)
    return True

@app.post(f"/register_new_user")
async def register_new_user(response: Response, credentials:Credentials) -> bool:
    new_user = client.new_user(username=credentials.username, password=credentials.password, email=credentials.email)
    user_id =client.get_user_id_by_username(username=credentials.username)
    thread_id = client.generate_thread_id()
    response.headers["thread_id"] = str(thread_id)
    response.headers["user_id"] = str(user_id)
    return new_user 

@app.get("/characters_color_map")
@thread_id
async def get_characterss_color_map(request: Request):
    characters = [character.stem.lower() for character in Path('scenarios/stuck_in_elevator/characters').iterdir() if character.stem != "mc"]
    select_colors = colors[:len(characters)]
    character_color_map = {**{"user":"blue","all":"red"}, **{character:select_colors[index].lower() for index, character in enumerate(characters)}}
    return {"characters_color_map":character_color_map}

@app.get("/initial_prompt")
@thread_id
async def get_initial_prompt(request: Request) -> dict[str, list[Prompt]]:
    initial_prompt_history = [prompt for prompt in trigger_prompt_list if prompt.trigger_type == "initial"]
    thread_id = request.headers['thread_id']
    user_id = request.headers['user_id']
    username = client.get_username_by_user_id(user_id)
    dump_prompt_history = [prompt.model_dump() for prompt in initial_prompt_history]
    client.new_conversation(username=username, thread_id=thread_id, user_id=user_id, initial_conversation=dump_prompt_history)
    return {"response": initial_prompt_history}

@app.post("/trigger_prompt")
@thread_id
async def trigger_prompt(request: Request,  prompt_history: list[Prompt]) -> dict[str, list[Prompt]]:
    try:
        #breakpoint()
        #thread_id = request.headers['thread_id']
        #prompt_history = [Prompt(**prompt) for prompt in client.get_conversation_by_thread_id(thread_id)]
        prompt =  random.choice([prompt for prompt in trigger_prompt_list if prompt.trigger_type == "trigger"])
        prompt_history.append(prompt)
        response = await get_response(prompt_history, vector_store_dict)
        dump_response = [prompt.model_dump() for prompt in response]
        client.update_conversation_by_thread_id(thread_id=request.headers['thread_id'], message_list=dump_response)
        return {"response":response}
    except Exception as e:
        print(f"Error handling prompt: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
@app.post("/handle_prompt")
@thread_id
async def handle_prompt(request: Request, prompt_history: list[Prompt]) -> dict[str, list[Prompt]]:
    try:
        response = await get_response(prompt_history, vector_store_dict)
        dump_response = [prompt.model_dump() for prompt in response]
        client.update_conversation_by_thread_id(thread_id=request.headers['thread_id'], message_list=dump_response)
        return {"response":response}
    except Exception as e:
        print(f"Error handling prompt: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


#Serve static files from /frontend/dist
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    print("Starting Uvicorn server")
    uvicorn.run(app, host="0.0.0.0", port=80)
