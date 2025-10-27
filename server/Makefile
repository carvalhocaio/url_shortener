lint:
	ruff check . && ruff check . --diff

format:
	ruff check . --fix && ruff format .

dev:
	uvicorn app.main:app --reload

build:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

# Docker commands for test database
docker-up-test-db:
	docker compose -f docker-compose.test.yml up -d
	@echo "Waiting for test database to be ready..."
	@sleep 3

docker-down-test-db:
	docker compose -f docker-compose.test.yml down -v

# Test commands
test:
	uv run pytest -v

test-cov:
	uv run pytest --cov=. --cov-report=html --cov-report=term

test-watch:
	uv run pytest-watch

# Run tests with test database (all-in-one command)
test-with-db:
	@make docker-up-test-db
	@make test || (make docker-down-test-db && exit 1)
	@make docker-down-test-db

# Pre-commit commands
pre-commit-install:
	uv run pre-commit install

pre-commit-uninstall:
	uv run pre-commit uninstall

pre-commit-run:
	uv run pre-commit run --all-files

pre-commit-update:
	uv run pre-commit autoupdate
