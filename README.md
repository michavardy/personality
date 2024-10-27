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
docker volume create sqlite_data
docker run -d -p 80:80 --name pc person -v sqlite_data:/app/data/records.db person
# Copy Key into database
```
## run app
```bash
http://167.99.134.62/
# interact with database
docker run --rm -it -v sqlite_data:/data alpine sh
```

## Remove Container
```bash
docker stop pc
docker container prune
docker image rm person
```