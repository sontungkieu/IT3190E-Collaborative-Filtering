# services/ui/demo.py
import gradio as gr
import requests

def get_recs(user_profile):
    resp = requests.post(
        "http://rec-service:8002/recommend",
        json={"user_profile": user_profile}
    ).json()
    return "\n".join(resp["recommendations"])

demo = gr.Interface(
    fn=get_recs,
    inputs=gr.Textbox(label="User Profile"),
    outputs=gr.Textbox(label="Recommendations"),
    title="E-Commerce Recommendation Demo"
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
