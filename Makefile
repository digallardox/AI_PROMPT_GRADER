.PHONY: run install run-no-refine

run:
	@echo "Checking for processes on port 8765..."
	@lsof -ti:8765 | xargs kill -9 2>/dev/null || true
	@echo "Starting server with message refinement enabled..."
	@echo "  ✓ ENABLE_REFINEMENT=true (configured in .env)"
	@echo "  ✓ Model: claude-3-5-haiku-20241022"
	@echo "  ✓ Timeout: 3.0s circuit breaker"
	@echo ""
	source venv/bin/activate && python -m app.main

run-no-refine:
	@echo "Checking for processes on port 8765..."
	@lsof -ti:8765 | xargs kill -9 2>/dev/null || true
	@echo "Starting server WITHOUT message refinement..."
	@echo "  ✗ ENABLE_REFINEMENT=false (temporary override)"
	@echo ""
	source venv/bin/activate && ENABLE_REFINEMENT=false python -m app.main

install:
	pip install -r requirements.txt

test:
	promptfoo eval --no-cache --config=tests/promptfooconfig.yaml > /dev/null
	promptfoo view --yes > /dev/null