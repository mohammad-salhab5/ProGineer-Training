import os
import streamlit as st
from ask import ask_quran_bot

st.set_page_config(
    page_title="Quran RAG Assistant",
    page_icon="📖",
    layout="centered"
)

# ---------------- CSS ---------------- #

st.markdown("""
<style>

.main {
    background-color: #f6f5ef;
}

h1{
    text-align:center;
    color:#1B5E20;
}

.answer-box{
    background:#111111;
    color:white;
    padding:20px;
    border-radius:15px;
    border-left:7px solid #2E7D32;
    margin-bottom:20px;
    box-shadow:0px 4px 12px rgba(0,0,0,.25);
    font-size:18px;
    line-height:1.8;
}

.verse-card{
    background:#faf7ef;
    border:1px solid #d8cfb5;
    border-radius:15px;
    padding:20px;
    margin-top:15px;
    box-shadow:0px 2px 6px rgba(0,0,0,.08);
}

.verse-text{
    direction:rtl;
    text-align:right;
    font-size:30px;
    line-height:2.3;
    color:#222;
}

.reference{
    text-align:center;
    margin-top:15px;
    color:#1B5E20;
    font-weight:bold;
    font-size:18px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- Header ---------------- #

st.title("📖 Quran Assistant")

st.markdown(
"""
Ask your question in **Arabic**.

The assistant answers **only from the retrieved Quran verses**, and every answer includes its references.
"""
)

# ---------------- API KEY ---------------- #

if not os.getenv("GROQ_API_KEY"):
    st.error("❌ GROQ_API_KEY is missing.")
    st.stop()

# ---------------- Input ---------------- #

question = st.text_input(
    "Ask your question",
    placeholder="مثال: ما هي فضائل الصبر؟"
)

# ---------------- Ask ---------------- #

if st.button("🔍 Ask"):

    if not question.strip():
        st.warning("Please enter a question.")
        st.stop()

    try:

        with st.spinner("Searching verses and generating answer..."):

            answer, verses = ask_quran_bot(question)

        

        st.subheader("🤖 Answer")

        st.markdown(
            f"""
            <div class="answer-box">
            {answer}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.subheader("📚 Retrieved Verses")

        for verse in verses:

            st.markdown(
                f"""
                <div class="verse-card">

                <div class="verse-text">
                ﴿ {verse['text']} ﴾
                </div>

                <div class="reference">
                {verse['reference']}
                </div>

                </div>
                """,
                unsafe_allow_html=True
            )

    except Exception as e:

        st.error("Failed to contact the AI service.")

        st.exception(e)