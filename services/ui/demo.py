import gradio as gr
import requests
import ujson as json
from pathlib import Path
import ast

# --- Service Endpoints ---
USER_SVC = "http://user-service:8003"
PROD_SVC = "http://product-service:8001"
REC_SVC = "http://rec-service:8002"
REV_SVC = "http://review-service:8004"

# --- Load Local Metadata ---
# File is named meta_Electronics.csv but contains JSON-like lines
meta_path = Path("meta_Electronics.csv")
product_meta = {}
if meta_path.exists():
    with meta_path.open("r", encoding="utf-8") as mf:
        for line in mf:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                try:
                    obj = ast.literal_eval(line)
                except Exception:
                    continue
            asin = obj.get("asin")
            if asin:
                product_meta[asin] = obj

# --- Auth Function ---
def login(username, password):
    try:
        resp = requests.post(
            f"{USER_SVC}/login", data={"username": username, "password": password}
        )
        resp.raise_for_status()
        token = resp.json().get("access_token")
        return token, "Đăng nhập thành công"
    except Exception as e:
        return None, f"Đăng nhập thất bại: {e}"

# --- Fetch List of Products ---
def fetch_products(token):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    resp = requests.get(f"{PROD_SVC}/products", headers=headers)
    resp.raise_for_status()
    prods = resp.json()
    choices = []
    for p in prods:
        pid = p['id']
        title = p['name'] or pid
        choices.append(f"{pid}:{title}")
    return gr.update(choices=choices, value=choices[0] if choices else None)

# --- Load Details: HTML Image, Info, Reviews, Recommendations ---
def load_details(token, selection):
    if not token:
        return "", "", [["Vui lòng đăng nhập", "", "", ""]], ""
    if not selection:
        return "", "", [], ""
    asin, _ = selection.split(":", 1)
    headers = {"Authorization": f"Bearer {token}"}

    # Product metadata
    meta = product_meta.get(asin, {})
    image_url = meta.get("imUrl", "")
    title = meta.get("title", asin)
    desc = meta.get("description", "")
    # Build HTML for image and title
    if image_url:
        image_html = f"<img src='{image_url}' alt='Product Image' width='300'/><br/><b>{title}</b>"
    else:
        image_html = f"<b>{title}</b>"
    info_md = desc

    # Reviews
    try:
        rev_resp = requests.get(
            f"{REV_SVC}/reviews?asin={asin}&limit=10", headers=headers
        )
        rev_resp.raise_for_status()
        reviews = rev_resp.json()
        review_rows = [[r.get("reviewer"), r.get("rating"), r.get("title"), r.get("text")] for r in reviews]
    except Exception as e:
        review_rows = [[f"Error fetching reviews: {e}", "", "", ""]]

    # Recommendations
    try:
        rec_resp = requests.post(
            f"{REC_SVC}/recommend", json={"user_profile": asin}, headers=headers
        )
        rec_resp.raise_for_status()
        recs = rec_resp.json().get("recommendations", [])
        rec_text = "\n".join(recs)
    except Exception as e:
        rec_text = f"Error fetching recommendations: {e}"

    return image_html, info_md, review_rows, rec_text

# --- Build Gradio UI ---
with gr.Blocks() as demo:
    gr.Markdown("# E-Commerce Demo: Login + Product Details + Reviews + Recommendations")

    with gr.Tab("Đăng nhập"):
        username = gr.Textbox(label="Username")
        password = gr.Textbox(label="Password", type="password")
        token_output = gr.Textbox(label="JWT Token")
        login_status = gr.Textbox(label="Status")
        login_btn = gr.Button("Login")
        login_btn.click(fn=login, inputs=[username, password], outputs=[token_output, login_status])

    with gr.Tab("Product Details"):
        token_state = gr.State()
        # Update token state after login
        login_btn.click(lambda tok, stat: tok, inputs=[token_output, login_status], outputs=[token_state])

        prod_dropdown = gr.Dropdown(label="Chọn sản phẩm (ASIN:Title)", choices=[])
        load_products_btn = gr.Button("Load Products")
        load_products_btn.click(fn=fetch_products, inputs=[token_state], outputs=[prod_dropdown])

        product_image = gr.HTML(label="Product Image & Title")
        product_info = gr.Markdown(label="Product Description")
        review_table = gr.Dataframe(
            headers=["Reviewer", "Rating", "Title", "Text"],
            datatype=["str", "number", "str", "str"],
            label="Reviews"
        )
        rec_output = gr.Textbox(label="Recommendations")
        load_details_btn = gr.Button("Load Details")
        load_details_btn.click(
            fn=load_details,
            inputs=[token_state, prod_dropdown],
            outputs=[product_image, product_info, review_table, rec_output]
        )

    gr.Markdown("*Bạn cần đăng nhập, sau đó Load Products và Load Details.*")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
