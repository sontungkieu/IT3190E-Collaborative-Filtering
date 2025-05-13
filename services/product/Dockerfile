# services/product/Dockerfile
FROM python:3.10-slim
WORKDIR /app
RUN pip install fastapi uvicorn ujson
COPY app.py .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]
