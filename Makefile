.PHONY: install train test run streamlit lint

PYTHON ?= python

install:
	$(PYTHON) -m pip install -r requirements.txt

train:
	$(PYTHON) src/training/train_crop.py
	$(PYTHON) src/training/train_yield.py

test:
	$(PYTHON) -m pytest tests/ -v

run:
	$(PYTHON) app/main.py

streamlit:
	$(PYTHON) -m streamlit run dashboard/streamlit_app.py

lint:
	$(PYTHON) -m ruff check src app tests 2>nul || echo "Install ruff for linting"

frontend-install:
	cd frontend && npm install

frontend-dev:
	cd frontend && npm run dev

frontend-build:
	cd frontend && npm run build
