# FROM python:3.10-slim
# WORKDIR /app
# COPY . .

# # Cài dependencies
# RUN pip install -r requirements.txt
# # RUN pip install -r user/requirements.txt


# # Khởi chạy service trên cổng 8003
# CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8003"]

FROM python:3.10-slim

WORKDIR /app

# 1) Upgrade pip so it can pull the wheel
RUN pip install --upgrade pip

# 2) Install bcrypt wheel (no Rust required)
# RUN pip install bcrypt

# 3) Install your other deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["uvicorn","app:app","--host","0.0.0.0","--port","8003"]
