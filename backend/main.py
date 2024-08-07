import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .rag_prompt import create_prompt, chain
from .objects import rules, scenarios, PromptRequest, md_to_dict
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]  # Ensure logs go to stdout
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scenario_name = 'stuck_in_elevator'
scenario = scenarios[scenario_name]

@app.get("/rules")
async def get_rules():
    breakpoint()
    try:
        rules_text = Path('scenarios/rules.md').read_text()
        print(f"get rules: {rules_text}")
        return {"rules": rules_text}
    except Exception as e:
        print(f"Error reading rules: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/scenario")
async def get_scenario():
    try:
        scenario_text = Path('scenarios/stuck_in_elevator/scenario.md').read_text()
        print(f"get scenario: {scenario_text}")
        return {"scenario": scenario_text}
    except Exception as e:
        print(f"Error reading scenario: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/handle_prompt")
async def handle_prompt(request: PromptRequest):
    print(f'handle prompt: {request}')
    try:
        prompt = create_prompt(
            action=request.action,
            prompt=request.prompt,
            rules=rules,
            scenario=scenario,
            history=request.history
        )
        response = chain.run(prompt=prompt)
        return {"response": response}
    except Exception as e:
        print(f"Error handling prompt: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# Serve static files from /frontend/dist
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    print("Starting Uvicorn server")
    uvicorn.run(app, host="0.0.0.0", port=80)
