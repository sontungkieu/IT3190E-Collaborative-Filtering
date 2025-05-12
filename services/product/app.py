# services/product/app.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Product Service")

class Product(BaseModel):
    id: int
    name: str

# giả lập dữ liệu
PRODUCTS = [
    {"id": 1, "name": "GPU RTX 3080"},
    {"id": 2, "name": "Corsair Vengeance 16GB"},
    {"id": 3, "name": "Asus ROG Strix Z690"},
]

@app.get("/products")
def list_products():
    return PRODUCTS

@app.get("/products/{product_id}")
def get_product(product_id: int):
    for p in PRODUCTS:
        if p["id"] == product_id:
            return p
    return {"error": "Not found"}
