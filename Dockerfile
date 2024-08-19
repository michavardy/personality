# Stage 1: Build React Frontend
FROM node:18 AS build

# Set the working directory
WORKDIR /app/frontend

# Copy package.json and package-lock.json
COPY frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the frontend application code
COPY frontend/ .

# Build the React application
RUN npm run build

# Stage 2: Set up Python Backend
FROM python:3.11-slim AS backend

# Set the working directory
WORKDIR /app

# Copy the backend code
COPY backend /app/backend

# Copy the requirements file and install dependencies
COPY backend/requirements.txt /app/backend/
COPY scenarios /app/scenarios
COPY data /app/data/
RUN mkdir stores
RUN python -m pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy the frontend build output to the backend directory
COPY --from=build /app/frontend/dist /app/frontend/dist

# Set environment variables
ENV DB_PATH=/app/stores/test_store
#ENV  OPENAI_API_KEY=
RUN python /app/data/vector_database.py --from_file --db_path $DB_PATH

# Expose ports
EXPOSE 80

# Command to run the backend server
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "80", "--log-level", "debug"]
