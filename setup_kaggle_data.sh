#!/usr/bin/env bash
set -euo pipefail

# 0. Kiểm tra Kaggle credentials (giữ nguyên phần này nếu bạn đã có)
# … (như cũ)

# 1. Tạo thư mục data và sqlite
echo "→ Tạo thư mục data/ và data/sqlite/ nếu chưa có"
mkdir -p data
mkdir -p data/sqlite

# 2. Download dataset 5-core Amazon Electronics Reviews (giữ nguyên)

# 3. Download metadata từ SNAP
META_URL="https://snap.stanford.edu/data/amazon/productGraph/categoryFiles/meta_Electronics.json.gz"
if [ ! -f data/meta_Electronics.jsonl ]; then
  echo "→ Tải metadata sản phẩm từ Stanford SNAP"
  curl -L "$META_URL" -o data/meta_Electronics.json.gz
  echo "→ Giải nén metadata..."
  gunzip -f data/meta_Electronics.json.gz
  mv data/meta_Electronics.json data/meta_Electronics.jsonl
else
  echo "→ data/meta_Electronics.jsonl đã tồn tại, bỏ qua bước download metadata"
fi

echo "✅ Hoàn tất setup dữ liệu (reviews + metadata)."
