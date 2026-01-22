import streamlit as st
import uuid
from langchain_core.messages import HumanMessage

from database_backend import workflow

# -------------------------
# Utilities
# -------------------------
def generate_thread_id():
    return str(uuid.uuid4())

def add_thread(thread_id):
    if thread_id not in st.session_state.chat_threads:
        st.session_state.chat_threads.append(thread_id)

def reset_chat():
    st.session_state.thread_id = generate_thread_id()
    st.session_state.message_history = []
    add_thread(st.session_state.thread_id)

# -------------------------
# Session State Init
# -------------------------
if "chat_threads" not in st.session_state:
    st.session_state.chat_threads = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = generate_thread_id()

if "message_history" not in st.session_state:
    st.session_state.message_history = []

add_thread(st.session_state.thread_id)

# -------------------------
# UI
# -------------------------
st.sidebar.title("LangGraph Chatbot")

if st.sidebar.button("New Chat"):
    reset_chat()

st.sidebar.header("My Conversations")
for tid in st.session_state.chat_threads[::-1]:
    if st.sidebar.button(tid):
        st.session_state.thread_id = tid
        st.session_state.message_history = []

# -------------------------
# Chat Window
# -------------------------
config = {"configurable": {"thread_id": st.session_state.thread_id}}

for msg in st.session_state.message_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Type your message")

if user_input:
    # User message
    st.session_state.message_history.append(
        {"role": "user", "content": user_input}
    )
    with st.chat_message("user"):
        st.markdown(user_input)

    # AI response (streaming)
    with st.chat_message("assistant"):
        chunks = []
        for message, _ in workflow.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config=config,
            stream_mode="messages",
        ):
            if message.content:
                chunks.append(message.content)
                st.write(message.content)

        ai_text = "".join(chunks)

    st.session_state.message_history.append(
        {"role": "assistant", "content": ai_text}
    )
