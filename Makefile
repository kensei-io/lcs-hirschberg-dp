# Comandos del proyecto. "make" ejecuta los tests y los experimentos completos.

.PHONY: all test experiments quick plots lint format

all: test experiments

test:
	uv run pytest

experiments:
	uv run lcs-hirschberg-dp

quick:
	uv run lcs-hirschberg-dp --quick

plots:
	uv run lcs-hirschberg-dp --plots-only

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff format .