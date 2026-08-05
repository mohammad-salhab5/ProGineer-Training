import streamlit as st

from ask import ask_quran_bot

st.set_page_config(page_title="Quran RAG Chatbot", layout="centered")

st.title("📖 Quran Assistant")

st.write("Ask a question in Arabic. Answers are grounded in retrieved verses, always cited.")

question = st.text_input("Your question:")

if st.button("Ask") and question:

    with st.spinner("Searching verses and generating an answer..."):

        answer, verses = ask_quran_bot(question)

    st.subheader("Answer")

    st.write(answer)

    st.subheader("Retrieved Verses")

    for v in verses:

        st.markdown(f"**{v['reference']}**")

        st.write(v["text"])

        st.divider()

Run with:

poetry run streamlit run app.py
