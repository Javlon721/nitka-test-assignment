PROJECT_DIR := $(CURDIR)
PYTHON := python3
API_PORT := 8080
HTML_PORT := 8001


build: 
	@$(PYTHON) -m venv venv  
	@source venv/bin/activate && pip install -r requirements.txt

run:
	@uvicorn src.api.app:app --reload --port $(API_PORT)

extract:
	@PYTHONPATH=. $(PYTHON) "${PROJECT_DIR}/src/scripts/index.py"

html:
	@$(PYTHON) -m http.server $(HTML_PORT) --directory "${PROJECT_DIR}/src/templates/"