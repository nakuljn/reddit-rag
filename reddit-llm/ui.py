import streamlit as st
import requests

st.set_page_config(page_title="Reddit-Powered LLM", layout="centered")
st.title("Reddit-Powered LLM Q&A")
st.write("Ask a question and get answers powered by Reddit discussions and LLMs.")

with st.form("ask_form"):
    user_query = st.text_input("Your question:", max_chars=500)
    top_k = st.slider("Number of Reddit sources to use:", min_value=1, max_value=10, value=5)
    submitted = st.form_submit_button("Ask")

if submitted and user_query.strip():
    with st.spinner("Thinking..."):
        try:
            response = requests.post(
                "http://localhost:8000/ask",
                json={"query": user_query, "top_k": top_k},
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                st.success(data["answer"])
                st.markdown("---")
                st.markdown(f"**Sources ({data['total_sources']}):**")
                for src in data["sources"]:
                    url = src.get("url")
                    subreddit = src.get("subreddit")
                    score = src.get("score")
                    st.markdown(f"- [{subreddit}]({url}) (score: {score})")
            else:
                st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
        except Exception as e:
            st.error(f"Request failed: {str(e)}") 