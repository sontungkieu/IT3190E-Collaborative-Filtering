# services/recommendation/app.py
from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI(title="Recommendation Service")

class RecRequest(BaseModel):
    user_profile: str

@app.post("/recommend")
def recommend(req: RecRequest):
    # ví dụ gọi product service để lấy danh sách
    prods = requests.get("http://product-service:8001/products").json()
    # chỉ chọn top-3 làm demo
    recs = [p["name"] for p in prods][:3]
    return {"recommendations": recs}
