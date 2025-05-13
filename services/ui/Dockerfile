# services/ui/Dockerfile
FROM python:3.10-slim
WORKDIR /app
RUN pip install gradio requests ujson
COPY demo.py .
CMD ["python", "demo.py"]
