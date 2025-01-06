.PHONY: clean cli server

SERVICE := lucy
PORT    := 8000

all: cli

cli:
	@echo "[🤖 CLI] Starting $(SERVICE)'s repl..."
	uv run cli.py --command='repl'

server:
	@echo "[🤖 SERVER] Starting $(SERVICE) on port $(PORT)..."
	uv run fastapi dev app/web.py

clean:
	@echo "Deleting all __pycache_/..."
	@find . \( -name ".mypy_cache" -o -name "__pycache__" -o -name "*.pyc" -o -name "*.pyo" \) -exec rm -rf {} +
