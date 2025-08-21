import gradio as gr
import os
from dotenv import load_dotenv
from app.main import generate_answer_with_context

load_dotenv()

async def ask_question_direct(message, top_k, model):
    if not message.strip():
        return "Please enter a question."
    
    try:
        result = await generate_answer_with_context(message, int(top_k), model)
        answer = result.answer
        
        if result.total_sources > 0:
            answer += f"\n\n**Sources ({result.total_sources}):**\n"
            for i, src in enumerate(result.sources, 1):
                answer += f"{i}. [r/{src.subreddit}]({src.url}) (score: {src.score})\n"
        
        return answer
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}. Please try again."

# Minimal CSS for dark theme
css = """
.gradio-container {
    background: #0f1419 !important;
    color: #ffffff !important;
}
.dark {
    background: #0f1419 !important;
}
footer {
    display: none !important;
}
"""

def handle_message(user_message, chat_history, state):
    """Handle user message and get bot response"""
    if not user_message.strip():
        return chat_history, state, ""
    
    # Add user message to chat
    chat_history.append([user_message, None])
    
    # Get settings from state
    top_k_val = state.get("top_k", 5)
    model_val = state.get("model", "grok")
    
    # Get bot response
    import asyncio
    try:
        bot_response = asyncio.run(ask_question_direct(user_message, top_k_val, model_val))
        chat_history[-1][1] = bot_response
    except Exception as e:
        chat_history[-1][1] = f"Sorry, I encountered an error: {str(e)}"
    
    return chat_history, state, ""

def update_settings(model, sources, state):
    """Update settings in state"""
    state["model"] = model
    state["top_k"] = sources
    return state

def clear_chat():
    """Clear the chat history"""
    return []

def set_prompt(prompt_text):
    """Set a suggested prompt"""
    return prompt_text

# Create the Gradio interface using Blocks
with gr.Blocks(title="Reddit RAG Assistant", theme=gr.themes.Soft(primary_hue="blue"), css=css) as demo:
    
    # Initialize state
    state = gr.State({"model": "grok", "top_k": 5})
    
    gr.Markdown("# 🤖 Reddit Knowledge Assistant")
    gr.Markdown("Ask me anything about Reddit communities, trends, and discussions")
    
    with gr.Row():
        # Left sidebar
        with gr.Column(scale=1):
            gr.Markdown("### ➕ NEW CHAT")
            clear_btn = gr.Button("Clear Chat", variant="secondary", size="sm")
            
            gr.Markdown("### ▼ TRY ASKING:")
            
            prompt1 = gr.Button("How does Reddit work?", size="sm")
            prompt2 = gr.Button("Popular subreddits", size="sm") 
            prompt3 = gr.Button("Building karma tips", size="sm")
            prompt4 = gr.Button("Trending discussions", size="sm")
            
            gr.Markdown("### ⚙️ SETTINGS")
            
            model_choice = gr.Radio(
                choices=["claude", "grok"],
                value="grok",
                label="AI Model"
            )
            
            top_k = gr.Slider(
                minimum=1,
                maximum=10,
                value=5,
                step=1,
                label="Number of Sources"
            )
        
        # Main chat area
        with gr.Column(scale=3):
            # Chat interface
            chatbot = gr.Chatbot(
                height=600,
                show_label=False,
                bubble_full_width=False
            )
            
            # Input area
            with gr.Row():
                user_input = gr.Textbox(
                    placeholder="Ask about Reddit communities, trending topics, or specific discussions...",
                    show_label=False,
                    scale=4,
                    lines=1,
                    max_lines=3
                )
                send_btn = gr.Button("🚀", scale=0, variant="primary")
    
    # Event handlers
    
    # Handle message submission
    user_input.submit(
        handle_message,
        inputs=[user_input, chatbot, state],
        outputs=[chatbot, state, user_input]
    )
    
    send_btn.click(
        handle_message,
        inputs=[user_input, chatbot, state],
        outputs=[chatbot, state, user_input]
    )
    
    # Handle settings changes
    model_choice.change(
        update_settings,
        inputs=[model_choice, top_k, state],
        outputs=[state]
    )
    
    top_k.change(
        update_settings,
        inputs=[model_choice, top_k, state],
        outputs=[state]
    )
    
    # Clear chat
    clear_btn.click(clear_chat, outputs=[chatbot])
    
    # Suggested prompts
    prompt1.click(set_prompt, outputs=[user_input]).then(
        lambda: "How does Reddit work?", outputs=[user_input]
    )
    prompt2.click(set_prompt, outputs=[user_input]).then(
        lambda: "What are the most popular subreddits?", outputs=[user_input]
    )
    prompt3.click(set_prompt, outputs=[user_input]).then(
        lambda: "How can I build karma on Reddit?", outputs=[user_input]
    )
    prompt4.click(set_prompt, outputs=[user_input]).then(
        lambda: "What are the current trending discussions?", outputs=[user_input]
    )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )