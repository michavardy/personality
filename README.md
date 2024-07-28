# personality

## Development
```bash
# activate virtual env
source backend/personality/Scripts/activate
# start uvicorn
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
# test prompt
python backend/prompt.py
# start react
cd frontend
npm run dev
```