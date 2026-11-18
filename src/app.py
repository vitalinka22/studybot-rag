"""Day 6: StudyBot as a web chat in the browser.

Start from the project folder:  streamlit run src/app.py
"""
import time
import uuid

import streamlit as st

from answer import respond
from conversation_log import save_turn

CONDITIONS = ["normal", "incomplete", "incorrect"]

st.set_page_config(page_title="StudyBot - TU Berlin", page_icon="🎓")
st.title("🎓 StudyBot")
st.caption("Ask me about study programs, admission and studying at TU Berlin. "
           "My answers are based on the TU Berlin website. "
           "Conversations are saved anonymously for a bachelor thesis study.")

condition = st.query_params.get("condition", "normal")
if condition not in CONDITIONS:
    condition = "normal"

if "history" not in st.session_state:
    st.session_state.history = []
    st.session_state.session_id = uuid.uuid4().hex

for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Type your question ...")
if question:
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        with st.spinner("Searching the TU Berlin website ..."):
            started = time.time()
            try:
                result = respond(question, st.session_state.history, condition)
            except Exception as error:
                print(f"ERROR in session {st.session_state.session_id}: {error}")
                st.error("Sorry, something went wrong. Please try again in a moment.")
                st.stop()
            seconds = round(time.time() - started, 1)
        st.markdown(result["reply"])

    turn = len(st.session_state.history) // 2 + 1
    save_turn(st.session_state.session_id, turn, question, result, seconds)

    st.session_state.history.append({"role": "user", "content": question})
    st.session_state.history.append({"role": "assistant", "content": result["reply"]})