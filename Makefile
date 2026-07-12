.PHONY: dev backend frontend

backend:
	cd server && uv run fastapi dev app/main.py

frontend:
	cd client && npm run dev

dev:
	$(MAKE) -j2 backend frontend
