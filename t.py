# client.py

import requests
import json

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

# === HÀM TEST ===

def test_single():
    sample = "Đây là ví dụ văn bản để test embedding."
    print("Gửi lên /embed:", sample)
    emb = embed_text(sample)
    if emb:
        print(f"Kích thước embedding: {len(emb)}")
        print("Một vài chiều đầu tiên của vector embedding:", emb[:10])
    else:
        print("Embed thất bại hoặc trả về rỗng")

# === PHẦN CHÍNH ===

def main():
    print("=== Test Embed Một Chuỗi ===")
    test_single()

if __name__ == "__main__":
    main()
