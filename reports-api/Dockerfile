FROM python:3.12-slim

WORKDIR /app

COPY app /app

RUN pip install asyncio cachetools fastapi httpx python-jose[cryptography] uvicorn

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
