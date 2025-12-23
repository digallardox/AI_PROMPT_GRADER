.PHONY: run install

run:
	@echo "Checking for processes on port 8765..."
	@lsof -ti:8765 | xargs kill -9 2>/dev/null || true
	@echo "Starting server..."
	source venv/bin/activate && python -m app.main

install:
	pip install -r requirements.txt

test:
	promptfoo eval --no-cache --config=tests/promptfooconfig.yaml > /dev/null
	promptfoo view --yes > /dev/null