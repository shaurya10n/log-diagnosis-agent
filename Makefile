.PHONY: run ingest test

run:
	docker compose up --build

ingest:
	docker compose exec app python scripts/ingest_docs.py

test:
	@echo "No tests configured yet."
