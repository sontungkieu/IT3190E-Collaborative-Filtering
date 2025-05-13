FROM python:3.10-slim
WORKDIR /app

# Cài dependencies
RUN pip install fastapi uvicorn sqlmodel passlib[bcrypt] pyjwt python-multipart 

COPY app.py .

# Khởi chạy service trên cổng 8003
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8003"]
