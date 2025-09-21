PROJECT_DIR := $(CURDIR)

build: 
	@uv sync

run: build
	@uvicorn src.api.app:app --reload

extract: build
	@PYTHONPATH=. uv run "${PROJECT_DIR}/src/scripts/index.py"

html: build
	@python3 -m http.server 8001 --directory "${PROJECT_DIR}/src/templates/"