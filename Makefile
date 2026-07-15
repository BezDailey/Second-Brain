.PHONY: dev backend frontend

backend:
	-lsof -tiTCP:8000 -sTCP:LISTEN | xargs kill -9 2>/dev/null || true
	cd server && PYTHONUNBUFFERED=1 uv run fastapi dev app/main.py

frontend:
	-lsof -tiTCP:5173 -sTCP:LISTEN | xargs kill -9 2>/dev/null || true
	cd client && npm run dev

dev:
	$(MAKE) -j2 backend frontend
