import os
import html
import time
import streamlit as st
from ask import ask_quran_bot


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Quran Assistant",
    page_icon="📖",
    layout="centered",
    initial_sidebar_state="expanded",
)


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []  # list[dict]: question, answer, verses, error

if "theme" not in st.session_state:
    st.session_state.theme = "light"

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None


def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"


def queue_example(example_text: str):
    st.session_state.pending_prompt = example_text


def clear_conversation():
    st.session_state.messages = []


# =========================================================
# THEME TOKENS
# =========================================================
# Refined teal-green palette: calmer, higher contrast, less saturated
# than the original bright-green scheme, aimed at a professional,
# modern reading experience.

if st.session_state.theme == "dark":
    T = {
        "bg": "#0c1210",
        "bg_radial": "rgba(29, 158, 117, 0.08)",
        "surface": "#121915",
        "surface_alt": "#182019",
        "border": "#232e28",
        "border_soft": "#1c2621",
        "text": "#eaf1ec",
        "text_dim": "#9bab9f",
        "text_faint": "#67766d",
        "accent": "#1d9e75",
        "accent_strong": "#146e53",
        "accent_soft": "rgba(29, 158, 117, 0.14)",
        "user_bubble": "#17251f",
        "assistant_bubble": "#121915",
        "shadow": "0 6px 18px rgba(0, 0, 0, 0.35)",
        "input_bg": "#121915",
    }
else:
    T = {
        "bg": "#f5f6f2",
        "bg_radial": "rgba(15, 110, 86, 0.06)",
        "surface": "#ffffff",
        "surface_alt": "#eef1ec",
        "border": "#dde3db",
        "border_soft": "#e6eae2",
        "text": "#182420",
        "text_dim": "#55645b",
        "text_faint": "#8b968d",
        "accent": "#0f6e56",
        "accent_strong": "#085041",
        "accent_soft": "rgba(15, 110, 86, 0.08)",
        "user_bubble": "#e1f5ee",
        "assistant_bubble": "#ffffff",
        "shadow": "0 6px 18px rgba(0, 0, 0, 0.05)",
        "input_bg": "#ffffff",
    }


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    f"""
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&family=Amiri:wght@400;700&display=swap');

    /* ---------- Global ---------- */

    html, body, [class*="css"] {{
        font-family: "Tajawal", "Segoe UI", "Noto Naskh Arabic", -apple-system, sans-serif;
    }}

    .stApp {{
        background:
            radial-gradient(circle at top, {T['bg_radial']}, transparent 40%),
            {T['bg']};
        color: {T['text']};
        transition: background 0.3s ease, color 0.3s ease;
    }}

    /* Main content area: use more of the laptop screen, less dead
       whitespace around the central card. */
    .block-container {{
        max-width: 1080px;
        padding-top: 0.9rem;
        padding-bottom: 6rem;
        padding-left: 1.4rem;
        padding-right: 1.4rem;
    }}

    @media (min-width: 1280px) {{
        .block-container {{ max-width: 1180px; }}
    }}

    @media (min-width: 1600px) {{
        .block-container {{ max-width: 1320px; }}
    }}

    #MainMenu, footer {{visibility: hidden;}}

    * {{
        scrollbar-width: thin;
    }}

    /* ---------- Header ---------- */

    .hero {{
        text-align: center;
        padding: 4px 10px 16px 10px;
    }}

    .hero-icon {{
        font-size: 34px;
        margin-bottom: 2px;
    }}

    .hero-title {{
        font-size: 27px;
        font-weight: 800;
        color: {T['accent_strong']};
        margin: 0;
        letter-spacing: -0.3px;
    }}

    .hero-subtitle {{
        color: {T['text_dim']};
        font-size: 14.5px;
        margin-top: 6px;
        line-height: 1.7;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }}

    .hero-badge {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: {T['accent_soft']};
        color: {T['accent_strong']};
        font-size: 12px;
        font-weight: 700;
        padding: 4px 13px;
        border-radius: 999px;
        margin-bottom: 10px;
    }}

    /* ---------- Sidebar ---------- */
    /* Narrower, tidier sidebar so it doesn't dominate the viewport. */

    section[data-testid="stSidebar"] {{
        background: {T['surface']};
        border-right: 1px solid {T['border']};
        min-width: 270px !important;
        max-width: 290px !important;
    }}

    section[data-testid="stSidebar"] > div {{
        padding-top: 0.6rem;
    }}

    section[data-testid="stSidebar"] * {{
        color: {T['text']} !important;
    }}

    section[data-testid="stSidebar"] .block-container {{
        padding-left: 0.9rem;
        padding-right: 0.9rem;
        padding-top: 0.4rem;
    }}

    .sidebar-title {{
        font-size: 16px;
        font-weight: 800;
        color: {T['accent_strong']} !important;
        margin-bottom: 2px;
    }}

    .sidebar-desc {{
        color: {T['text_dim']} !important;
        font-size: 12.5px;
        line-height: 1.65;
        direction: rtl;
        text-align: right;
        margin-top: 2px;
    }}

    .sidebar-caption {{
        color: {T['text_faint']} !important;
        font-size: 11px;
        text-align: center;
    }}

    section[data-testid="stSidebar"] div.stButton > button {{
        width: 100%;
        text-align: right;
        direction: rtl;
        background: {T['surface_alt']};
        border: 1px solid {T['border']};
        color: {T['text']} !important;
        border-radius: 10px;
        font-size: 12.5px;
        font-weight: 600;
        padding: 8px 12px;
        margin-bottom: 5px;
        min-height: auto;
        line-height: 1.4;
        transition: 0.15s ease;
        box-shadow: none;
    }}

    section[data-testid="stSidebar"] div.stButton > button:hover {{
        border-color: {T['accent']};
        background: {T['accent_soft']};
        transform: translateX(-2px);
    }}

    section[data-testid="stSidebar"] hr {{
        margin: 0.7rem 0 !important;
    }}

    .theme-toggle button {{
        background: {T['accent_soft']} !important;
        border: 1px solid {T['accent']} !important;
        font-weight: 700 !important;
        padding: 4px 10px !important;
    }}

    /* ---------- Chat messages ---------- */

    div[data-testid="stChatMessage"] {{
        background: transparent;
        padding: 4px 0;
        animation: fadeIn 0.3s ease;
    }}

    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(6px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}

    /* user bubble */
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {{
        direction: rtl;
    }}

    .user-bubble {{
        background: {T['user_bubble']};
        color: {T['text']};
        border: 1px solid {T['border_soft']};
        border-radius: 16px 16px 4px 16px;
        padding: 12px 16px;
        direction: rtl;
        text-align: right;
        font-size: 15.5px;
        line-height: 1.75;
        display: inline-block;
        max-width: 100%;
    }}

    /* ---------- Answer card ---------- */

    .answer-box {{
        background: {T['accent_strong']};
        color: #ffffff;
        padding: 16px 20px;
        border-radius: 16px 16px 16px 4px;
        box-shadow: {T['shadow']};
        direction: rtl;
        text-align: right;
        font-size: 16px;
        line-height: 1.85;
    }}

    .answer-label {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        color: rgba(255,255,255,0.82);
        font-size: 12px;
        font-weight: 700;
        margin-bottom: 6px;
        letter-spacing: 0.2px;
    }}

    /* ---------- Section labels ---------- */

    .section-title {{
        color: {T['text_dim']};
        font-size: 12.5px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 14px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 6px;
        direction: rtl;
    }}

    /* ---------- Verse Card ---------- */

    .verse-card {{
        background: {T['surface']};
        border: 1px solid {T['border']};
        border-radius: 14px;
        padding: 16px 18px;
        margin: 8px 0;
        box-shadow: {T['shadow']};
        transition: transform 0.15s ease;
    }}

    .verse-card:hover {{
        transform: translateY(-1px);
    }}

    .verse-number {{
        display: inline-block;
        background: {T['accent_soft']};
        color: {T['accent_strong']};
        padding: 3px 11px;
        border-radius: 999px;
        font-size: 11.5px;
        font-weight: 700;
        margin-bottom: 11px;
    }}

    .verse-text {{
        direction: rtl;
        text-align: right;
        font-family: "Amiri", "Noto Naskh Arabic", serif;
        font-size: 23px;
        line-height: 2.15;
        color: {T['text']};
    }}

    .reference {{
        text-align: center;
        margin-top: 12px;
        padding-top: 10px;
        border-top: 1px solid {T['border_soft']};
        color: {T['accent_strong']};
        font-weight: 800;
        font-size: 13.5px;
        direction: rtl;
    }}

    /* ---------- Typing indicator ---------- */

    .typing-wrap {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: {T['surface_alt']};
        border: 1px solid {T['border']};
        border-radius: 16px 16px 16px 4px;
        padding: 12px 18px;
        direction: rtl;
    }}

    .typing-label {{
        font-size: 13px;
        color: {T['text_dim']};
        margin-left: 8px;
    }}

    .dot {{
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: {T['accent']};
        animation: bounce 1.2s infinite ease-in-out;
    }}

    .dot:nth-child(2) {{ animation-delay: 0.15s; }}
    .dot:nth-child(3) {{ animation-delay: 0.3s; }}

    @keyframes bounce {{
        0%, 60%, 100% {{ transform: translateY(0); opacity: 0.5; }}
        30% {{ transform: translateY(-5px); opacity: 1; }}
    }}

    /* ---------- Empty state ---------- */

    .empty-state {{
        text-align: center;
        padding: 34px 22px;
        background: {T['surface']};
        border-radius: 18px;
        border: 1px dashed {T['border']};
        color: {T['text_dim']};
        margin-top: 6px;
    }}

    .empty-state-icon {{
        font-size: 34px;
        margin-bottom: 8px;
    }}

    .empty-state-title {{
        font-size: 16.5px;
        font-weight: 800;
        color: {T['text']};
        margin-bottom: 5px;
    }}

    .empty-state-sub {{
        font-size: 13.5px;
        color: {T['text_faint']};
        direction: rtl;
    }}

    /* ---------- Error card ---------- */

    .error-card {{
        background: {T['surface']};
        border: 1px solid #e0625c;
        border-right: 4px solid #d64541;
        border-radius: 14px;
        padding: 14px 18px;
        color: {T['text']};
        direction: rtl;
        text-align: right;
        font-size: 14px;
        line-height: 1.75;
    }}

    .error-title {{
        color: #d64541;
        font-weight: 800;
        font-size: 14px;
        margin-bottom: 4px;
    }}

    /* ---------- No verses card ---------- */

    .no-verses {{
        text-align: center;
        padding: 18px 16px;
        background: {T['surface']};
        border-radius: 14px;
        border: 1px dashed {T['border']};
        color: {T['text_dim']};
        font-size: 13.5px;
        direction: rtl;
    }}

    /* ---------- Chat input ---------- */

    div[data-testid="stChatInput"] {{
        background: {T['input_bg']};
        border: 1px solid {T['border']};
        border-radius: 16px;
        box-shadow: {T['shadow']};
    }}

    div[data-testid="stChatInput"] textarea {{
        direction: rtl;
        text-align: right;
        font-size: 15.5px;
        color: #ffffff !important;
        color: {T['text']};
    }}

    div[data-testid="stChatInput"] button {{
        background: {T['accent_strong']} !important;
        border-radius: 12px !important;
    }}

    /* ---------- Footer ---------- */

    .footer {{
        text-align: center;
        color: {T['text_faint']};
        font-size: 12px;
        margin-top: 28px;
        padding-top: 14px;
        border-top: 1px solid {T['border_soft']};
    }}

    /* ---------- Mobile ---------- */

    @media (max-width: 600px) {{

        .block-container {{
            padding-left: 0.85rem;
            padding-right: 0.85rem;
        }}

        .hero-title {{
            font-size: 23px;
        }}

        .hero-subtitle {{
            font-size: 13.5px;
        }}

        .verse-text {{
            font-size: 20px;
            line-height: 2.05;
        }}

        .answer-box {{
            font-size: 14.5px;
            padding: 14px;
        }}

    }}

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-badge">✨ مدعوم بتقنية RAG</div>
        <div class="hero-icon">📖</div>
        <div class="hero-title">مساعد القرآن الكريم</div>
        <div class="hero-subtitle">
            اسأل سؤالك باللغة العربية، وسيبحث المساعد في آيات القرآن
            ذات الصلة ويعرض لك الإجابة مع المراجع.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    top_col1, top_col2 = st.columns([3, 1])

    with top_col1:
        st.markdown('<div class="sidebar-title">📖 Quran Assistant</div>', unsafe_allow_html=True)

    with top_col2:
        st.markdown('<div class="theme-toggle">', unsafe_allow_html=True)
        st.button(
            "🌙" if st.session_state.theme == "light" else "☀️",
            on_click=toggle_theme,
            key="theme_toggle_btn",
            help="تبديل الوضع الداكن / الفاتح",
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="sidebar-desc">
        يستخدم هذا التطبيق تقنية <b>RAG</b> للبحث عن الآيات القرآنية
        المرتبطة بسؤالك ثم توليد إجابة اعتمادًا على الآيات المسترجعة.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown('<div class="sidebar-title" style="font-size:13px;">💡 أمثلة</div>', unsafe_allow_html=True)

    examples = [
        "ما هي فضائل الصبر؟",
        "ماذا يقول القرآن عن بر الوالدين؟",
        "ما هي صفات المؤمنين؟",
        "ماذا ورد عن التوبة؟",
    ]

    for i, example in enumerate(examples):
        st.button(example, key=f"example_{i}", on_click=queue_example, args=(example,))

    st.divider()

    if st.session_state.messages:
        st.button("🗑️ مسح المحادثة", on_click=clear_conversation, use_container_width=True)
        st.divider()

    st.markdown('<div class="sidebar-caption">Quran RAG Assistant</div>', unsafe_allow_html=True)


# =========================================================
# API KEY CHECK
# =========================================================

if not os.getenv("GROQ_API_KEY"):

    st.error(
        "⚠️ لم يتم العثور على GROQ_API_KEY. "
        "يرجى إضافته إلى متغيرات البيئة قبل تشغيل التطبيق."
    )

    st.stop()


# =========================================================
# RENDER HELPERS
# =========================================================

def render_user_turn(question: str):
    with st.chat_message("user", avatar="🧑"):
        safe_q = html.escape(str(question))
        st.markdown(f'<div class="user-bubble">{safe_q}</div>', unsafe_allow_html=True)


def render_assistant_turn(answer=None, verses=None, error=None):
    with st.chat_message("assistant", avatar="📖"):

        if error:
            st.markdown(
                f"""
                <div class="error-card">
                    <div class="error-title">❌ حدث خطأ</div>
                    {html.escape(error)}
                </div>
                """,
                unsafe_allow_html=True,
            )
            return

        safe_answer = html.escape(str(answer))

        st.markdown(
            f"""
            <div class="answer-box">
                <div class="answer-label">🤖 إجابة مبنية على الآيات المسترجعة</div>
                {safe_answer}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="section-title">📚 الآيات المسترجعة</div>',
            unsafe_allow_html=True,
        )

        if verses:

            st.caption(f"تم العثور على {len(verses)} آية مرتبطة بسؤالك.")

            for index, verse in enumerate(verses, start=1):

                verse_text = html.escape(str(verse.get("text", "")))
                reference = html.escape(str(verse.get("reference", "")))

                st.markdown(
                    f"""
                    <div class="verse-card">
                        <div class="verse-number">آية {index}</div>
                        <div class="verse-text">﴿ {verse_text} ﴾</div>
                        <div class="reference">{reference}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        else:

            st.markdown(
                """
                <div class="no-verses">
                    <div style="font-size:26px;">🔍</div>
                    <strong>لم يتم العثور على آيات مناسبة.</strong>
                    <br>جرّب صياغة السؤال بطريقة مختلفة.
                </div>
                """,
                unsafe_allow_html=True,
            )


# =========================================================
# CONVERSATION
# =========================================================

if not st.session_state.messages:

    st.markdown(
        """
        <div class="empty-state">
            <div class="empty-state-icon">💬</div>
            <div class="empty-state-title">ابدأ محادثتك الآن</div>
            <div class="empty-state-sub">
                اكتب سؤالك في الأسفل أو اختر أحد الأمثلة من القائمة الجانبية
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

else:

    for turn in st.session_state.messages:
        render_user_turn(turn["question"])
        render_assistant_turn(
            answer=turn.get("answer"),
            verses=turn.get("verses"),
            error=turn.get("error"),
        )


# =========================================================
# INPUT
# =========================================================

prompt = st.chat_input("اكتب سؤالك عن القرآن الكريم هنا...")
  # Set the button color to accent color

if not prompt and st.session_state.pending_prompt:
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

if prompt and prompt.strip():

    question = prompt.strip()

    render_user_turn(question)

    with st.chat_message("assistant", avatar="📖"):

        placeholder = st.empty()

        placeholder.markdown(
            """
            <div class="typing-wrap">
                <span class="typing-label">جاري البحث عن الآيات المناسبة</span>
                <span class="dot"></span><span class="dot"></span><span class="dot"></span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        turn = {"question": question, "answer": None, "verses": None, "error": None}

        try:
            answer, verses = ask_quran_bot(question)
            turn["answer"] = answer
            turn["verses"] = verses

        except Exception  as e:
            print(f"❌ ERROR in ask_quran_bot: {e}") 
            turn["error"] = "حدث خطأ أثناء معالجة السؤال. يرجى المحاولة مرة أخرى."

        placeholder.empty()

    st.session_state.messages.append(turn)
    st.rerun()


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        📖 Quran RAG Assistant
        <br>
        البحث والاستجابة اعتمادًا على الآيات المسترجعة
    </div>
    """,
    unsafe_allow_html=True,
)