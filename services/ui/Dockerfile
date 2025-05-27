# services/ui/Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . .
# RUN pip install -r ui/requirements.txt
RUN pip install -r requirements.txt
CMD ["python", "demo.py"]
