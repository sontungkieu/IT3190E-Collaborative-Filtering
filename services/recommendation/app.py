# services/recommendation/app.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI(title="Recommendation Service")

# CORS: cho phép frontend http://localhost:3000 truy cập
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RecRequest(BaseModel):
    user_profile: str

@app.post("/recommend")
def recommend(req: RecRequest):
    # 1) Lấy history từ User Service
    try:
        sh_resp = requests.get(f"http://user-service:8003/users/{req.user_profile}/history/search")
        vh_resp = requests.get(f"http://user-service:8003/users/{req.user_profile}/history/view")
        sh = sh_resp.ok and sh_resp.json() or []
        vh = vh_resp.ok and vh_resp.json() or []
    except Exception:
        sh, vh = [], []

    # 2) Lấy toàn bộ metadata sản phẩm
    prods = requests.get("http://product-service:8001/products").json()

    # 3) Dummy: chọn top-k theo thứ tự list, dùng 'title' làm tên hiển thị
    k = 20
    recs = []
    for p in prods[:k]:
        # ưu tiên trường 'title', fallback sang 'asin'
        recs.append(p.get("title") or p.get("asin"))

    return {
        "recommendations": recs,
        "search_history": sh,
        "view_history": vh
    }
