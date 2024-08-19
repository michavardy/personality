# personality

## Install Development Environment
```bash
sudo python3.11 -m venv personality  # create virtual environment

```

## Development
```bash
# activate virtual env
source backend/personality/Scripts/activate
# test vector store
python data/test_vector_store.py
# test response_flow
python  python backend/character_agents.py
# start uvicorn
uvicorn backend.main:app --reload --host 0.0.0.0 --port 80
# test prompt
python backend/prompt.py
# start react
cd frontend
npm run dev
```

## build container
```bash
docker build -t person .
docker run -d -p 80:80 --name pc person
# Copy Key into database
#docker run --env-file .env -d -p 80:80 --name pc person
docker stop pc
docker container prune
docker image rm person
```