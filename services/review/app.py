import ujson as json
from fastapi import FastAPI, HTTPException, Query
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional, List

# --- Model ---
class Review(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    review_id: str = Field(index=True)
    product_id: str = Field(index=True)
    reviewer: str
    rating: float
    title: str
    text: str

# --- Database setup ---
# lưu file reviews.db vào thư mục /app/db (đảm bảo thư mục đã mount)
DATABASE_URL = "sqlite:///./db/reviews.db"
engine = create_engine(DATABASE_URL, echo=False)
SQLModel.metadata.create_all(engine)

# --- FastAPI app ---
app = FastAPI(title="Review Service (Electronics 5-core)")

@app.on_event("startup")
def load_reviews():
    # Nếu đã có record thì bỏ qua import
    with Session(engine) as session:
        existing = session.exec(select(Review).limit(1)).first()
        if existing:
            print("✔️ Reviews already loaded, skipping import.")
            return

    # Import file reviews.jsonl → SQLite
    count = 0
    with open("reviews.jsonl", "r", encoding="utf-8") as f, Session(engine) as session:
        for line in f:
            obj = json.loads(line)
            rev = Review(
                review_id = obj.get("reviewerID", ""),
                product_id= obj.get("asin", ""),
                reviewer  = obj.get("reviewerName") or "Anonymous",
                rating    = float(obj.get("overall", 0.0)),
                title     = obj.get("summary",""),
                text      = obj.get("reviewText","")
            )
            session.add(rev)
            count += 1
            # commit theo batch 10k records để tránh dùng quá nhiều RAM
            if count % 10000 == 0:
                session.commit()
                print(f"  → Imported {count} reviews…")
        session.commit()
    print(f"✅ Finished loading {count} reviews into SQLite.")

# --- API endpoint ---
@app.get("/reviews", response_model=List[Review])
def get_reviews(
    asin: str = Query(..., description="Product ASIN"),
    limit: int = Query(10, ge=1, le=100)
):
    with Session(engine) as session:
        stmt = select(Review).where(Review.product_id == asin).limit(limit)
        results = session.exec(stmt).all()
    if not results:
        raise HTTPException(status_code=404, detail=f"No reviews for ASIN={asin}")
    return results
