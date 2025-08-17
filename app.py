import gradio as gr
import requests
import os
import subprocess
import threading
import time

# Configure API base URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

def start_backend():
    """Start FastAPI backend in background"""
    print("🚀 Starting FastAPI backend...")
    subprocess.Popen(["python", "-m", "app.main"])
    time.sleep(10)  # Wait for backend to start
    print("✅ Backend started")

def respond(message, history, top_k):
    """Send question to FastAPI backend and return response"""
    if not message.strip():
        return history, ""
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/ask",
            json={"query": message, "top_k": int(top_k)},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            answer = data["answer"]
            
            # Format sources
            if data.get('total_sources', 0) > 0:
                answer += f"\n\n**Sources ({data['total_sources']}):**\n"
                for i, src in enumerate(data["sources"], 1):
                    url = src.get("url", "")
                    subreddit = src.get("subreddit", "")
                    score = src.get("score", 0)
                    answer += f"{i}. [r/{subreddit}]({url}) (score: {score})\n"
            
            # Add to chat history
            history.append([message, answer])
            return history, ""
        else:
            error_msg = f"Error: {response.json().get('detail', 'Unknown error')}"
            history.append([message, error_msg])
            return history, ""
    except Exception as e:
        error_msg = f"Request failed: {str(e)}"
        history.append([message, error_msg])
        return history, ""

# Create ChatGPT-style conversational interface
with gr.Blocks(title="Ask Reddit") as demo:
    gr.Markdown("# 🤖 Ask Reddit")
    gr.Markdown("*Have a conversation powered by Reddit discussions and AI*")
    
    with gr.Row():
        with gr.Column(scale=4):
            # Chat interface
            chatbot = gr.Chatbot(
                label="Chat",
                height=500,
                show_label=False
            )
            
            with gr.Row():
                msg = gr.Textbox(
                    placeholder="Type your message here...",
                    show_label=False,
                    scale=4
                )
                send_btn = gr.Button("Send", variant="primary", scale=1)
        
        with gr.Column(scale=1):
            # Sidebar with settings
            gr.Markdown("### Settings")
            top_k = gr.Slider(
                minimum=1,
                maximum=10,
                value=5,
                step=1,
                label="Sources"
            )
            clear_btn = gr.Button("Clear Chat", variant="secondary")
    
    # Event handlers
    def user_message(message, history):
        return "", history + [[message, None]]
    
    def bot_response(history, top_k_val):
        if history and history[-1][1] is None:
            message = history[-1][0]
            try:
                response = requests.post(
                    f"{API_BASE_URL}/ask",
                    json={"query": message, "top_k": int(top_k_val)},
                    timeout=30
                )
                if response.status_code == 200:
                    data = response.json()
                    answer = data["answer"]
                    
                    if data.get('total_sources', 0) > 0:
                        answer += f"\n\n**Sources ({data['total_sources']}):**\n"
                        for i, src in enumerate(data["sources"], 1):
                            url = src.get("url", "")
                            subreddit = src.get("subreddit", "")
                            score = src.get("score", 0)
                            answer += f"{i}. [r/{subreddit}]({url}) (score: {score})\n"
                    
                    history[-1][1] = answer
                else:
                    history[-1][1] = f"Error: {response.json().get('detail', 'Unknown error')}"
            except Exception as e:
                history[-1][1] = f"Request failed: {str(e)}"
        
        return history
    
    # Wire up the events
    msg.submit(user_message, [msg, chatbot], [msg, chatbot]).then(
        bot_response, [chatbot, top_k], chatbot
    )
    send_btn.click(user_message, [msg, chatbot], [msg, chatbot]).then(
        bot_response, [chatbot, top_k], chatbot
    )
    clear_btn.click(lambda: [], None, chatbot)

if __name__ == "__main__":
    # Start backend in a separate thread
    threading.Thread(target=start_backend, daemon=True).start()
    
    # Launch Gradio frontend
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )