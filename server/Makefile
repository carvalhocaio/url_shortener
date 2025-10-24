lint:
	ruff check . && ruff check . --diff

format:
	ruff check . --fix && ruff format .

dev:
	fastapi dev main.py

run:
	fastapi dev main.py

build:
	uv run fastapi run main.py
