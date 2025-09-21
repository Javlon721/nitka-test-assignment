PROJECT_DIR := $(CURDIR)

run:
	@uvicorn src.api.app:app --reload

extract:
	@PYTHONPATH=. uv run "${PROJECT_DIR}/src/scripts/index.py"

html:
	@python3 -m http.server 8001 --directory "${PROJECT_DIR}/src/templates/"