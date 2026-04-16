# ReAssist Setup Guide

## Prerequisites
- Python 3.10+
- Node.js 18+
- Docker & Docker Compose (optional for local deployment)
- OpenAI API Key

## Environment Setup
Copy the `.env.example` file to create your local `.env`:
```bash
cp .env.example .env
```
Ensure you update the `OPENAI_API_KEY` placeholder.

## Local Execution
### 1. Backend
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e .[dev]

uvicorn src.api.app:app --reload --port 8000
```
### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```

## Docker Deployment
Using the provided `docker-compose.yml`, you can spin up the full stack (PostgreSQL + FastAPI + NextJS).
```bash
make docker-up
```
