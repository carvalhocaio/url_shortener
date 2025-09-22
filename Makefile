lint:
	ruff check . && ruff check . --diff

format:
	ruff check . --fix && ruff format .

run:
	...
