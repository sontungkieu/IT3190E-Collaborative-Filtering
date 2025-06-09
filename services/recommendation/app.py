# services/recommendation/app.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from typing import Dict, Any, List


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

class SearchRequest(BaseModel):
    query: str


# === CẤU HÌNH ===
# Thay YOUR_NGROK_URL bằng URL ngrok bạn vừa in ra ở Kaggle, ví dụ:
#   https://abcd1234-fgh.ngrok.io
# (Không có dấu "/" ở cuối)
NGROK_URL = "https://7378-34-91-110-183.ngrok-free.app"  # <-- sửa lại cho đúng

# === HÀM GỌI API ===

def embed_text(text: str) -> list:
    """
    Gửi 1 chuỗi text lên endpoint /embed, trả về embedding (list of floats).
    Nếu lỗi (status != 200), hàm sẽ in ra lỗi và return [].
    """
    endpoint = f"{NGROK_URL}/embed"
    payload = {"text": text}
    try:
        resp = requests.post(endpoint, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("embedding", [])
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Gọi /embed thất bại: {e}")
        return []
    except ValueError:
        print("[ERROR] Phản hồi không phải JSON hợp lệ")
        return []

t1 = [
    {
      "text": "keyboard "*10,
      "created_at": "2025-05-30T05:25:46.787770"
    },
    # {
    #   "text": "mouse "*10,
    #   "created_at": "2025-05-30T05:05:54.306232"
    # }
  ]
t2 =[
    # {
    #   "text": "Dell",
    #   "created_at": "2025-05-30T05:42:50.728827"
    # },
    # {
    #   "text": "logitech",
    #   "created_at": "2025-05-30T05:42:46.493915"
    # }
  ]

def export_text(t1,t2,use_t2= False):
    """
    """
    res = "user's interest:\n"
    for id,u in enumerate(t1):
        t = u.get("text", "")
        if t!="":
            t += " "
        res += t*max(0,10-id*2) + "\n"
    if use_t2:
        for id,u in enumerate(t2):
            t = u.get("text", "")
            if t!="":
                t += " "
            res += t*max(0,10-id*2) + "\n"
    return res

import json
import numpy as np
import requests

# ================================================================
# 1. Định nghĩa hàm để load JSON và trả về all_texts, all_embeds, all_norms
# ================================================================

def load_embeddings_from_json(
    json_path: str,
    blacklist: list[str] = None,
    normalize: bool = False,
    overwrite: bool = False
):
    """
    Đọc file JSON (ví dụ: output_embeddings.json) có cấu trúc:
    {
        "text2embed": {
            "Some text A": [0.12, -0.53, ...],
            "Some text B": [0.45,  0.22, ...],
            ...
        }
    }
    Thêm 2 tham số:
      • normalize (bool): 
          - Nếu False (mặc định), giữ embedding gốc.
          - Nếu True, tính vector chuẩn hóa (unit vector = v / ||v||).
      • overwrite (bool):
          - Nếu False (mặc định), KHÔNG ghi đè file JSON.
          - Nếu True, ghi đè file JSON với các vector (gốc hoặc chuẩn hóa tuỳ normalize).
    
    Ngoài ra cho phép truyền thêm `blacklist` gồm các từ (hoặc cụm từ).
    Nếu text chứa bất kỳ từ nào trong blacklist (so sánh case-insensitive), sẽ bỏ qua text đó.

    Trả về:
      - filtered_texts: list[str] (các văn bản đã lọc)
      - all_embeds: np.ndarray shape (N, D) chứa embedding gốc tương ứng
      - all_norms:  np.ndarray shape (N,) là norm (||v||) của mỗi embedding gốc
    """
    # 1) Thiết lập blacklist mặc định nếu không truyền vào
    if blacklist is None:
        blacklist = [
            "lumiquest", "Compatible", "14&quot;", "ColorMunki",
            "Cleaning", "Timer", "Shoe", "slim case", "Livescribe",
            "COVER", "Android 4.0", "Purple", "Cinema", "Earphone",
            "computer lock", "Decals", "Projector", "VGA", "530T",
            "AAA", "Lithium", "Remote Control", "batter", "Antec One",
            "Picture", "case", "Pctv", "Strip", "Mp3", "EM60", "phone", 
            "Speaker", "StarTech.com", "Kensington",
            "Headset", "OtterBox", "Speaker", "Cleaner", "eReader", "DVI", 
            "Slinglink", "Pogoplug","Patchbay","Protection","Bag", "NETWORK", 
            "Keyspan", "Multimedia", "Mountable", "150m",
            "Crumpler", "OmniMount", "MartinLogan", "pack", "clik", "rouge", 
            "Vanguard","tumi", "tv",
            "hde", "ibuy", "sound","quis","++","wacom","dock","11g","plug","brunton", "tiny", "s75c",
            "mercury", "contour", "cobra", "jiggler", "HDMI", "menotek", "riteav", "sumd", "rogue","att","savvy","lacie","escort","golf",
            "wifi","duo","tomtom","silicon","mirro","rf","labeler","cooler",
            "jump","mount","ematic","fidelity","skin",
        ]
    # Chuẩn hóa blacklist về lowercase để so sánh không phân biệt hoa/thường
    blacklist_lower = [term.lower() for term in blacklist]

    # 2) Đọc toàn bộ JSON
    with open(json_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    text2embed = raw.get("text2embed", {})
    print(f"Loaded {len(text2embed)} texts from {json_path}.")

    filtered_texts = []
    filtered_embeds = []
    # Dùng để lưu các vector (gốc hoặc chuẩn hóa) nếu cần overwrite
    new_map: dict[str, list[float]] = {}

    # 3) Lọc theo blacklist và tính norm + (tuỳ chọn normalize)
    for text, embed_list in text2embed.items():
        text_lower = text.lower()
        # Nếu text chứa bất kỳ term nào trong blacklist_lower, skip
        skip = False
        for term in blacklist_lower:
            if term in text_lower:
                skip = True
                break
        if skip:
            continue

        # Chuyển embed_list thành numpy array
        raw_vec = np.array(embed_list, dtype=np.float32)
        norm = np.linalg.norm(raw_vec)
        if norm == 0:
            # Nếu vector gốc có độ dài 0, ta skip luôn (không thể normalize)
            continue

        # Lưu embedding gốc
        filtered_texts.append(text)
        filtered_embeds.append(raw_vec)

        # Tính vector để ghi nếu overwrite=True
        if normalize:
            norm_vec = (raw_vec / norm).tolist()
            new_map[text] = norm_vec
        else:
            # Không normalize, giữ nguyên gốc
            new_map[text] = raw_vec.tolist()

    # 4) Chuyển danh sách embedding gốc thành numpy array shape (N, D)
    if filtered_embeds:
        all_embeds = np.stack(filtered_embeds, axis=0)  # shape (N, D)
        all_norms = np.linalg.norm(all_embeds, axis=1)  # shape (N,)
    else:
        # Trường hợp không còn embedding nào sau lọc
        all_embeds = np.empty((0, 0), dtype=np.float32)
        all_norms = np.empty((0,), dtype=np.float32)

    print(f"Filtered down to {len(filtered_texts)} texts after applying blacklist.")
    print(f"Shape of all_embeds: {all_embeds.shape}")
    print(f"Shape of all_norms: {all_norms.shape}")

    # 5) Nếu overwrite=True, ghi đè file JSON với các vector đã chọn
    if overwrite:
        updated_content = {"text2embed": new_map}
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(updated_content, f, ensure_ascii=False, indent=2)
        print(f"✅ Overwrote JSON file '{json_path}' with {'normalized' if normalize else 'original'} vectors.")

    # 6) Trả về danh sách đã lọc cùng embedding gốc và norms
    return filtered_texts, all_embeds, all_norms





# ================================================================
# 2. Hàm phụ: tìm top-k văn bản dựa trên cosine similarity
# ================================================================
def find_top_k_texts(user_embedding: np.ndarray,
                     all_texts: list,
                     all_embeds: np.ndarray,
                     all_norms: np.ndarray,
                     k: int = 20) -> list:
    """
    Input:
      - user_embedding: np.ndarray shape (D,)
      - all_texts: list các chuỗi tương ứng với each row of all_embeds
      - all_embeds: np.ndarray shape (N, D)
      - all_norms:  np.ndarray shape (N,) là ||embedding_i||
      - k: số lượng kết quả cần trả về
    Output:
      - list[str]: top-k text có cosine similarity cao nhất với user_embedding
    """
    user_vec = np.array(user_embedding, dtype=np.float32).reshape(-1)
    user_norm = np.linalg.norm(user_vec)
    if user_norm == 0:
        return []

    dots = all_embeds.dot(user_vec)  # shape (N,)
    eps = 1e-8
    sims = dots / (all_norms * user_norm + eps)  # shape (N,)

    # Lấy top-k indices
    N = sims.shape[0]
    if k >= N:
        topk_idx = np.argsort(-sims)
    else:
        topk_idx = np.argpartition(-sims, k)[:k]
        topk_idx = topk_idx[np.argsort(-sims[topk_idx])]

    return [all_texts[i] for i in topk_idx]



# ================================================================
# 3. Hàm get_recommendations_real, tích hợp phần load file JSON bên trong
# ================================================================
def get_recommendations(user_profile: str, testing=False) -> dict:
    """
    Core logic:
      1) Fetch search_history (sh) và view_history (vh) từ User Service.
         Nếu lỗi thì sh, vh = [].
      2) Nếu testing=True, bạn có thể override sh, vh bằng dữ liệu mẫu.
      3) Dùng export_text(sh, vh) để tạo user_text, rồi embed_text(user_text) để được user_embedding.
      4) Load file output_embeddings.json (data/output_embeddings.json) để có all_texts, all_embeds, all_norms.
      5) Gọi find_top_k_texts để lấy 20 text gợi ý gần nhất.
      6) Trả về dict gồm: recommendations, search_history, view_history.
    """
    # 1) Lấy history từ User Service
    # 1) Lấy history từ User Service
    try:
        sh_resp = requests.get(f"http://user-service:8003/users/{user_profile}/history/search")
        vh_resp = requests.get(f"http://user-service:8003/users/{user_profile}/history/view")
        sh = sh_resp.ok and sh_resp.json() or []
        vh = vh_resp.ok and vh_resp.json() or []
    except Exception:
        sh, vh = [], []

    # 2) Nếu đang test, override bằng t1, t2 (nếu bạn đã định nghĩa t1, t2 ở đâu đó)
    if testing:
        # Ví dụ: từ module khác import t1, t2
        # from your_module import t1, t2
        sh = t1
        vh = t2
        # pass

    # 3) Đưa lịch sử thành 1 chuỗi văn bản, rồi embed
    user_text = export_text(sh, vh)
    print(f"User text: {user_text}")
    user_embedding = embed_text(user_text)  # numpy array shape (D,)
    print(f"User embedding: {user_embedding}")

    # 4) Load toàn bộ embeddings từ file JSON
    #    Giả sử file đã được download trước và nằm ở data/output_embeddings.json
    EMBED_PATH = "output_embeddings.json"
    all_texts, all_embeds, all_norms = load_embeddings_from_json(EMBED_PATH)

    # 5) Tìm 20 text gợi ý gần nhất
    topk = 20
    recommendations = find_top_k_texts(
        user_embedding, all_texts, all_embeds, all_norms, k=topk
    )

    # 6) Trả về kết quả
    return {
        "recommendations": recommendations,
        "search_history": sh,
        "view_history": vh
    }



@app.post("/recommend")
def recommend_endpoint(req: RecRequest):
    # endpoint lấy đúng dict do get_recommendations trả về
    resp = get_recommendations("user")
    print(f"Recommendations for {req.user_profile}: completed")
    return resp

# =================== PHẦN MỚI: /search endpoint ====================
@app.post("/search")
def search_endpoint(req: SearchRequest) -> Dict[str, List[str]]:
    """
    Nhận JSON: { "query": "<chuỗi search>" }
    1) Tính embedding cho req.query bằng embed_text
    2) Load embeddings từ file (cũng dùng load_embeddings_from_json)
    3) Dùng find_top_k_texts(query_embedding, ...) để lấy 20 'texts' gần nhất
    4) Trả về JSON: { "search_results": [ list of text ] }
    """

    query_text = req.query
    if not query_text or not query_text.strip():
        return {"search_results": []}
    query_text = (query_text.strip()+" ")*10
    # 1) Tính embedding cho query
    try:
        query_embedding = embed_text(query_text)  # numpy array shape (D,)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cannot embed query: {e}")

    # 2) Load embeddings
    EMBED_PATH = "output_embeddings.json"
    all_texts, all_embeds, all_norms = load_embeddings_from_json(EMBED_PATH)

    if all_embeds.size == 0:
        return {"search_results": []}

    # 3) Tìm top-20 closest texts
    topk = 20
    search_results = find_top_k_texts(query_embedding, all_texts, all_embeds, all_norms, k=topk)

    # 4) Trả về array of strings
    return {"search_results": search_results}
