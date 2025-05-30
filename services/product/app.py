import sqlite3
import ast
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from typing import Dict, List, Any
from pathlib import Path

app = FastAPI(title="Product Service with Metadata")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)


# Paths
db_path = Path("db/reviews.db")
meta_path = Path("meta_Electronics.csv")  # Each line is a Python dict or JSON string

# ASIN -> title mapping
metadata_map: Dict[str, Dict[str, any]] = {}

@app.on_event("startup")
def load_metadata():
    if not meta_path.exists():
        print(f"⚠️ Metadata file {meta_path} not found. Using ASIN as fallback.")
        return
    count = 0
    with meta_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = ast.literal_eval(line)
            except Exception:
                try:
                    data = json.loads(line)
                except Exception:
                    continue
            asin = data.get("asin")
            if not asin:
                continue
            metadata_map[asin] = data
            count += 1
    print(f"✅ Loaded metadata for {count} products from {meta_path}")

@app.get("/products", response_model=List[Dict[str, Any]])
def list_products():
    if not db_path.exists():
        raise HTTPException(status_code=500, detail="Database not initialized.")
    try:
        conn = sqlite3.connect(str(db_path), check_same_thread=False)
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT product_id FROM Review")
        rows = [r[0] for r in cur.fetchall()]
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")
    finally:
        conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail="No products found.")

    products = []
    for pid in rows:
        prod = metadata_map.get(pid)
        if not prod:
            # fallback simple object
            prod = {"asin": pid}
        products.append(prod)
    return products