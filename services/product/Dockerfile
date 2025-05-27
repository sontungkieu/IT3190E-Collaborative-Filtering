# services/product/Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
# RUN pip install -r product/requirements.txt
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]
