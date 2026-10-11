"""Streamlit web UI for the Resume Chatbot.  Run: streamlit run app.py"""
import streamlit as st
from chatbot import ResumeBot

st.set_page_config(page_title="Resume Chatbot", page_icon="🤖", layout="centered")


@st.cache_resource
def load_bot():
    return ResumeBot()


bot = load_bot()

st.title("🤖 Resume Chatbot")
st.caption(f"Ask anything about {bot.profile['name']}  •  Mode: {bot.mode}")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant",
         "content": f"Hi! I'm {bot.name}'s resume assistant. Ask me about his skills, "
                    "projects, education or experience."}
    ]

with st.sidebar:
    st.header("💡 Try asking")
    clicked = None
    for q in bot.suggestions():
        if st.button(q, use_container_width=True):
            clicked = q
    if st.button("🗑 Clear chat", use_container_width=True):
        st.session_state.messages = st.session_state.messages[:1]
        st.rerun()

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

prompt = st.chat_input("Type your question...") or clicked
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    reply = bot.answer(prompt)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
