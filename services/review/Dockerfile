FROM python:3.10-slim
WORKDIR /app

COPY . .
# Cài FastAPI, Uvicorn, SQLModel và ujson
# RUN pip install fastapi uvicorn sqlmodel ujson

# RUN pip install -r review/requirements.txt
RUN pip install -r requirements.txt


CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8004"]
