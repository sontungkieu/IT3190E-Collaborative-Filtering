FROM python:3.10-slim
WORKDIR /app

# Cài FastAPI, Uvicorn, SQLModel và ujson
RUN pip install fastapi uvicorn sqlmodel ujson

COPY app.py .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8004"]
