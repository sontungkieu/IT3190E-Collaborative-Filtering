import sqlite3
import ast
import json
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

# ASIN -> metadata mapping (including title)
metadata_map: Dict[str, Dict[str, Any]] = {}

# Define a blacklist of terms: nếu title chứa bất kỳ từ nào trong list này (case-insensitive),
# sẽ không xuất sản phẩm đó trong response.
blacklist =  ["lumiquest", "Compatible", "14&quot;", "ColorMunki", "Cleaning", "Timer", 
              "Shoe", "slim case", "Livescribe", "COVER", "Android 4.0", "Purple", "Cinema", 
              "Earphone", "computer lock", "Decals", "Projector", "VGA", "530T", "AAA", "Lithium", 
              "Remote Control", "batter", "Antec One", "Picture", "case","Pctv" ,"noble", "arm", 
              "nook", "olympus", "bushnell", "california", "external", "truck","sawyer", "3g", "kindle",
              "db9", "yamakasi", "mygica", "bargain", "moleskine", "grade", "maxell", "ge", "palmone", 
              "rca", "outdoor", "streambot", "aaa", "streambot", "lizone", "wpa4220kit", "allreli", 
              "iclever", "34w", "inateck&reg;", "saicoo&trade;", "sharkk&reg;", "yens&reg;", 
              "taotronics&reg;", "bolse&reg;", "jetech&reg;", "amp", "flash&trade;",
                 "aerb&reg;", "supernight&reg;", "hypario&reg;", "mnxo&reg;", "digiyes&reg;", 
                 "bearextender", "dbpower", "avatar", "cable", "microphone", "radio", "ipod", 
                 "82mm", "dvd", "cd", "targus", "apc", "memorex", "diamond", "palm", "Strip", 
                 "Mp3", "EM60", "phone","Strip", "Mp3", "EM60", "phone", "Speaker", "StarTech.com", "Kensington",
            "Headset", "OtterBox", "Speaker", "Cleaner", "eReader", "DVI", 
            "Slinglink", "Pogoplug","Patchbay","Protection","Bag", "NETWORK", "Keyspan", 
            "Multimedia", "Mountable", "150m", 
            "Crumpler", "OmniMount", "MartinLogan", "pack", "clik", "rouge", "Vanguard","tumi", "tv",
            "hde", "ibuy", "sound","quis","++","wacom","dock","11g","plug","brunton", "tiny", "s75c",]

  # Thêm các từ/cụm từ bạn muốn lọc ở đây
blacklist_lower = [term.lower() for term in blacklist]


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
        prod_meta = metadata_map.get(pid)
        if prod_meta:
            title = prod_meta.get("title", "")
            title_lower = title.lower()
            # Kiểm tra xem title có chứa term nào thuộc blacklist không
            skip = False
            for term in blacklist_lower:
                if term in title_lower:
                    skip = True
                    break
            if skip:
                continue  # Bỏ qua sản phẩm này nếu title chứa từ cấm
            
            products.append(prod_meta)
        else:
            # Nếu không có metadata, fallback chỉ chứa ASIN (không có title để kiểm tra)
            products.append({"asin": pid})

    if not products:
        raise HTTPException(status_code=404, detail="No products found after applying blacklist filter.")

    return products
