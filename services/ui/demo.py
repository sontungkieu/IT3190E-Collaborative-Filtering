# services/ui/demo.py
import gradio as gr
import requests

USER_SVC = "http://user-service:8003"
PROD_SVC = "http://product-service:8001"
REC_SVC = "http://rec-service:8002"

def login(username, password):
    resp = requests.post(f"{USER_SVC}/login", data={"username": username, "password": password})
    if resp.status_code != 200:
        return None, "Đăng nhập thất bại"
    token = resp.json()["access_token"]
    return token, "Đăng nhập thành công"

def fetch_products(token):
    prods = requests.get(f"{PROD_SVC}/products").json()
    # Tạo danh sách choices kiểu "id: name"
    choices = [f"{p['id']}: {p['name']}" for p in prods]
    # Trả về object để Gradio cập nhật dropdown
    return gr.update(choices=choices, value=choices[0] if choices else None)

def recommend(token, selection):
    headers = {"Authorization": f"Bearer {token}"}
    # Lấy product_id từ chuỗi "id: name"
    product_id = selection.split(":")[0]
    resp = requests.post(
        f"{REC_SVC}/recommend",
        json={"user_profile": product_id},
        headers=headers
    )
    if resp.status_code != 200:
        return "Lỗi khi lấy gợi ý"
    return "\n".join(resp.json()["recommendations"])

with gr.Blocks() as demo:
    gr.Markdown("# E-Commerce Demo với Gradio và Microservices")

    with gr.Tab("Đăng nhập"):
        username = gr.Textbox(label="Username")
        password = gr.Textbox(label="Password", type="password")
        token_output = gr.Textbox(label="JWT Token")
        login_status = gr.Textbox(label="Status")
        login_btn = gr.Button("Login")
        login_btn.click(fn=login, inputs=[username, password], outputs=[token_output, login_status])

    with gr.Tab("Products & Recommendation"):
        token_state = gr.State()
        # Cập nhật token_state sau khi login
        login_btn.click(lambda t, s: t, inputs=[token_output, login_status], outputs=[token_state])

        prod_dropdown = gr.Dropdown(label="Chọn sản phẩm", choices=[])
        load_btn = gr.Button("Load Products")
        load_btn.click(fn=fetch_products, inputs=[token_state], outputs=[prod_dropdown])

        rec_output = gr.Textbox(label="Recommendations")
        rec_btn = gr.Button("Get Recommendation")
        rec_btn.click(fn=recommend, inputs=[token_state, prod_dropdown], outputs=[rec_output])

    gr.Markdown("*Bạn cần login trước khi load products và nhận gợi ý.*")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
