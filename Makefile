.PHONY: install etl train-models api dashboard test clean

install:
	python3.12 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

etl:
	python -m etl.pipeline

train-models:
	python -m models.train

api:
	uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

dashboard:
	PYTHONPATH=. streamlit run dashboards/app.py --server.port 8501

test:
	pytest

clean:
	rm -f data/database/*.db data/processed/*.csv data/processed/*.json logs/*.log models/metrics.json
	rm -rf models/artifacts
