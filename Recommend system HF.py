#!pip install -q sentence-transformers faiss-cpu

import pandas as pd
#%load_ext cuml.accel
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from collections import defaultdict
import faiss

# Load metadata và rating
df_meta = pd.read_csv("/kaggle/input/amazone-dataset-with-full-reviews/filtered_metadata (3).csv")
df_rating = pd.read_csv("/kaggle/input/amazone-dataset-with-full-reviews/train_ratings.csv")

valid_items = set(df_rating["item_id"])

df_meta = df_meta[df_meta["item_id"].isin(valid_items)].copy()

# Giữ các cột cần thiết
df_meta = df_meta[["description", "features", "categories", "price", "average_rating", "item_id", "store"]]
df_meta = df_meta.dropna(subset=["price", "item_id", "categories"])

# Tiền xử lý description
df_meta["price"] = pd.to_numeric(df_meta["price"], errors='coerce')
df_meta["average_rating"] = pd.to_numeric(df_meta["average_rating"], errors='coerce')

# Điền giá trị thiếu bằng median (hoặc bạn có thể dùng mean, 0, v.v.)
df_meta["price"].fillna(df_meta["price"].median(), inplace=True)
df_meta["average_rating"].fillna(df_meta["average_rating"].median(), inplace=True)

# Chuẩn hóa numeric
scaler = MinMaxScaler()
df_meta["price_scaled"] = 0.0

# Lặp qua từng category để scale riêng
for cat in df_meta["categories"].unique():
    mask = df_meta["categories"] == cat
    df_meta.loc[mask, "price_scaled"] = scaler.fit_transform(df_meta.loc[mask, ["price"]])

# Tạo user-category matrix (binary: user có mua trong category)
df_join = df_rating.merge(df_meta[["item_id", "categories"]], on="item_id")
df_join = df_join.dropna(subset=["categories"])

user_cat = df_join.groupby(["user_id", "categories"]).size().reset_index(name="interaction")
user_cat["interaction"] = 1  # chỉ cần có tương tác

user_cat_matrix = user_cat.pivot(index="user_id", columns="categories", values="interaction").fillna(0)

from sklearn.neighbors import NearestNeighbors

# Ma trận nhị phân có thể dùng uint8 để giảm RAM
user_cat_matrix = user_cat_matrix.astype('uint8')

# Dùng brute-force với cosine distance
model_knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=100, n_jobs=-1)
model_knn.fit(user_cat_matrix)

# Tìm top 100 user tương tự cho mỗi user
distances, indices = model_knn.kneighbors(user_cat_matrix, n_neighbors=100)

# Map index lại
user_ids = user_cat_matrix.index.tolist()
similar_users = {
    user_ids[i]: [user_ids[j] for j in indices[i][1:]]  # bỏ chính mình ở vị trí 0
    for i in range(len(user_ids))
}

# Ghép vector SBERT + price
model = SentenceTransformer('all-MiniLM-L6-v2')
df_meta["text"] = df_meta["description"] + " " + df_meta["features"].fillna("")
text_embeddings = model.encode(df_meta["text"].tolist(), show_progress_bar=True)

final_features = np.hstack([
    text_embeddings,
    df_meta[["price_scaled"]].values
])

# FAISS indexing
index = faiss.IndexFlatL2(final_features.shape[1])
index.add(final_features)

# ID mapping
asin2idx = dict(zip(df_meta["item_id"], range(len(df_meta))))
idx2asin = dict(zip(range(len(df_meta)), df_meta["item_id"]))

def get_top_categories_for_user(user_id, topN=5, topK_users=100):
    if user_id not in user_cat_matrix.index:
        return []

    # Lấy vector tương tác của user
    user_vector = user_cat_matrix.loc[[user_id]]

    # Lấy topK_users + 1 (bao gồm cả chính user đó)
    distances, indices = model_knn.kneighbors(user_vector, n_neighbors=topK_users + 1)

    # Bỏ chính user_id khỏi danh sách
    top_user_indices = indices[0][1:]
    top_users = user_cat_matrix.index[top_user_indices]

    # Lọc các tương tác từ user tương tự
    sub = user_cat[user_cat["user_id"].isin(top_users)]

    # Tính tổng tương tác theo category
    category_scores = (
        sub.groupby("categories")["interaction"]
        .sum()
        .sort_values(ascending=False)
    )

    return category_scores.head(topN).index.tolist()

from collections import defaultdict

def recommend_items_for_user(user_id, topK=20, min_items_per_cat=3):
    top_cats = get_top_categories_for_user(user_id, topK_users=100)
    user_items = df_rating[df_rating["user_id"] == user_id]["item_id"].tolist()
    
    # 1. Lọc candidate theo top categories và chưa từng mua
    candidate_df = df_meta[
        (df_meta["categories"].isin(top_cats)) &
        (~df_meta["item_id"].isin(user_items)) &
        (df_meta["average_rating"] >= 4)
    ]

    # 2. Lấy embedding của các candidate
    candidate_indices = [asin2idx[asin] for asin in candidate_df["item_id"] if asin in asin2idx]
    candidate_vectors = final_features[candidate_indices]
    
    # 3. Tính vector hồ sơ người dùng
    bought_idx = [asin2idx[a] for a in user_items if a in asin2idx]
    if not bought_idx:
        return []
    user_vector = final_features[bought_idx].mean(axis=0, keepdims=True)

    # 4. FAISS: tìm topK*10 item gần nhất (để có đủ lựa chọn)
    D, I = index.search(user_vector, topK * 10)

    # 5. Giữ lại những item trong candidate_df
    top_recs = [idx2asin[i] for i in I[0] if idx2asin[i] in candidate_df["item_id"].values]

    # 6. Đảm bảo mỗi category có ít nhất min_items_per_cat, sau đó bổ sung nếu thiếu
    final = []
    cat_counts = defaultdict(int)
    used = set()

    for pid in top_recs:
        cat = df_meta[df_meta["item_id"] == pid]["categories"].values[0]
        if cat in top_cats and cat_counts[cat] < min_items_per_cat:
            final.append(pid)
            cat_counts[cat] += 1
            used.add(pid)
        if len(final) >= topK:
            break

    # 7. Nếu chưa đủ topK, bổ sung từ top_recs còn lại
    if len(final) < topK:
        for pid in top_recs:
            if pid not in used:
                final.append(pid)
                used.add(pid)
                if len(final) >= topK:
                    break

    return final

recommend_items_for_user("AHC6GN4R2TGIZBFZ5TY6OYRNVDIQ", topK=15, min_items_per_cat=3)