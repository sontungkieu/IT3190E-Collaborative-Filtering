#!/usr/bin/env bash
set -euo pipefail

# 0. Kiểm tra Kaggle credentials (giữ nguyên phần này nếu bạn đã có)
# … (như cũ)

# 1. Tạo thư mục data và sqlite
echo "→ Tạo thư mục data/ và data/sqlite/ nếu chưa có"
mkdir -p data
mkdir -p data/sqlite

# 2. Download dataset 5-core Amazon Electronics Reviews (giữ nguyên)

#!/usr/bin/env bash
set -euo pipefail

# 0. Kiểm tra Kaggle credentials
if [ ! -f "${HOME}/.kaggle/kaggle.json" ] && \
   ([ -z "${KAGGLE_USERNAME:-}" ] || [ -z "${KAGGLE_KEY:-}" ]); then
  echo "❌ Bạn chưa cấu hình Kaggle API. Vui lòng đặt ~/.kaggle/kaggle.json hoặc export KAGGLE_USERNAME & KAGGLE_KEY."
  exit 1
fi

# 1. Tạo thư mục data và sqlite
echo "→ Tạo thư mục data/ và data/sqlite/ nếu chưa có"
mkdir -p data
mkdir -p data/sqlite

# 2. Download dataset 5-core Amazon Electronics Reviews
DATASET="deniall/5core-amazon-electronics-reviews"
ZIPFILE="5core-amazon-electronics-reviews.zip"

if [ ! -f "data/Electronics-5core.jsonl" ]; then
  echo "→ Tải dataset ${DATASET} từ Kaggle"
  kaggle datasets download -d ${DATASET} -p data --unzip
  # Thành phẩm thường là reviews.jsonl hoặc 5core-amazon-electronics-reviews.zip rồi unzipped thành reviews.jsonl
  # Đổi tên cho đồng nhất
  if [ -f data/reviews_Electronics_5.json ]; then
    mv data/reviews_Electronics_5.json data/Electronics-5core.json
  elif [ -f data/Reviews.csv ]; then
    # nếu là CSV, chuyển qua JSONL (nếu cần)
    echo "→ Đổi Reviews.csv sang Electronics-5core.jsonl"
    tail -n +2 data/Reviews.csv | \
      awk -F',' '{print "{\"asin\":\""$1"\",\"reviewerID\":\""$2"\",\"overall\":"$3",\"reviewText\":\""$6"\"}"}' \
      > data/Electronics-5core.jsonl
  else
    echo "⚠️ Không tìm thấy reviews.jsonl hay Reviews.csv sau khi unzip"
    exit 1
  fi
else
  echo "→ data/Electronics-5core.jsonl đã tồn tại, bỏ qua bước download"
fi

# 3. (Tuỳ) Download metadata nếu cần
# Nếu bạn cần thêm meta_Electronics.jsonl từ SNAP:
# curl -L "https://snap.stanford.edu/data/amazon/productGraph/categoryFiles/meta_Electronics.json.gz" \
#    -o data/meta_Electronics.json.gz && gunzip -f data/meta_Electronics.json.gz

echo "✅ Hoàn tất set core5."



# 3. Download metadata từ SNAP
META_URL="https://snap.stanford.edu/data/amazon/productGraph/categoryFiles/meta_Electronics.json.gz"
if [ ! -f data/meta_Electronics.csv]; then
  echo "→ Tải metadata sản phẩm từ Stanford SNAP"
  curl -L "$META_URL" -o data/meta_Electronics.json.gz
  echo "→ Giải nén metadata..."
  gunzip -f data/meta_Electronics.json.gz
  mv data/meta_Electronics.json data/meta_Electronics.csv
else
  echo "→ data/meta_Electronics.jsonl đã tồn tại, bỏ qua bước download metadata"
fi

echo "✅ Hoàn tất setup dữ liệu (reviews + metadata)."
