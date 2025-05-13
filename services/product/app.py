import sqlite3
import ast
from fastapi import FastAPI, HTTPException
from typing import Dict, List
from pathlib import Path

app = FastAPI(title="Product Service with Metadata")

# Paths
db_path = Path("db/reviews.db")
meta_path = Path("meta_Electronics.csv")  # Each line is a Python dict or JSON string

# ASIN -> title mapping
titles_map: Dict[str, str] = {}

@app.on_event("startup")
def load_metadata():
    if not meta_path.exists():
        print(f"⚠️ Metadata file {meta_path} not found. Using ASIN as name.")
        return
    count = 0
    with meta_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                # Parse line as Python literal or JSON
                data = ast.literal_eval(line)
            except Exception:
                try:
                    import json
                    data = json.loads(line)
                except Exception:
                    continue
            asin = data.get("asin")
            # title field may vary
            title = data.get("title") or data.get("product_name") or data.get("name")
            if asin and title:
                titles_map[asin] = title
                count += 1
    print(f"✅ Loaded metadata for {count} products from {meta_path}")

@app.get("/products", response_model=List[Dict[str, str]])
def list_products():
    if not db_path.exists():
        raise HTTPException(status_code=500, detail="Database not initialized.")
    try:
        conn = sqlite3.connect(str(db_path), check_same_thread=False)
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT product_id FROM Review")
        rows = cur.fetchall()
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")
    finally:
        conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail="No products found.")

    products = []
    for (pid,) in rows:
        name = titles_map.get(pid) or pid
        products.append({"id": pid, "name": name})
    return products
