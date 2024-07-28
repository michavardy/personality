from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from .prompt import create_prompt, chain
from .objects import rules, scenarios,  PromptRequest, md_to_dict
from pathlib import Path

app = FastAPI()

scenario_name ='stuck_in_elevator'
scenario = scenarios[scenario_name]

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
    return {"rules": rules}

@app.get("/scenario")
async def get_scenario():
    return {"scenario": scenarios}

@app.post("/handle_prompt")
async def handle_prompt(request: PromptRequest):
    characters = {char.stem:md_to_dict(char.read_text()) for char in Path(f'scenarios/{scenario_name}/characters').iterdir() if char.stem != "mc"}
    prompt = create_prompt(
        action=request.action, 
        prompt=request.prompt, 
        rules=rules, 
        scenario=scenario, 
        characters=characters, 
        history=request.history
        )
    response = chain.run(prompt=prompt)
    return {"response": response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
