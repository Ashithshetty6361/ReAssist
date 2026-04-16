format:
	ruff format src/
lint:
	ruff check src/
test:
	pytest tests/ -v
typecheck:
	mypy src/ --ignore-missing-imports
dev:
	uvicorn src.api.app:app --reload --port 8000
docker-up:
	docker-compose up -d --build
