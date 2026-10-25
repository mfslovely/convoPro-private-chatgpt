"""Streamlit entry point for the private Ollama chat application."""

from html import escape
from typing import Any

import streamlit as st

from db.conversations import (
    add_message,
    create_new_conversation,
    get_all_conversations,
    get_conversation,
)
from llm_factory.get_llm import get_ollama_llm
from services.get_models_list import get_models_list
from services.get_title import get_title


st.set_page_config(
    page_title="ConvoPro · Private AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)


CUSTOM_CSS = """
<style>
    :root {
        --cp-bg: #07111f;
        --cp-panel: rgba(15, 27, 45, 0.82);
        --cp-panel-strong: rgba(19, 34, 55, 0.96);
        --cp-border: rgba(148, 163, 184, 0.17);
        --cp-text: #edf4ff;
        --cp-muted: #93a4bd;
        --cp-accent: #7c6cff;
        --cp-accent-two: #28c7b7;
    }

    .stApp {
        color: var(--cp-text);
        background:
            radial-gradient(circle at 18% 4%, rgba(124, 108, 255, 0.19), transparent 30rem),
            radial-gradient(circle at 82% 18%, rgba(40, 199, 183, 0.12), transparent 28rem),
            linear-gradient(145deg, #07111f 0%, #0a1423 48%, #07101c 100%);
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stMainBlockContainer"] {
        max-width: 900px;
        padding-top: 1.25rem;
        padding-bottom: 7rem;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(10, 20, 35, 0.98), rgba(8, 17, 30, 0.98));
        border-right: 1px solid var(--cp-border);
    }

    [data-testid="stSidebarContent"] {
        padding: 1.35rem 0.9rem 1.5rem;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {
        color: #dce7f5;
    }

    .cp-brand {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1.35rem;
    }

    .cp-brand-mark {
        display: grid;
        width: 2.55rem;
        height: 2.55rem;
        place-items: center;
        border: 1px solid rgba(255, 255, 255, 0.17);
        border-radius: 0.85rem;
        color: white;
        font-size: 1.2rem;
        background: linear-gradient(135deg, var(--cp-accent), #4d8fff);
        box-shadow: 0 10px 28px rgba(92, 83, 230, 0.32);
    }

    .cp-brand-name {
        color: var(--cp-text);
        font-size: 1.08rem;
        font-weight: 750;
        letter-spacing: -0.02em;
    }

    .cp-brand-subtitle {
        color: var(--cp-muted);
        font-size: 0.75rem;
    }

    .cp-status {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        margin: 0.35rem 0 1rem;
        padding: 0.68rem 0.78rem;
        border: 1px solid rgba(40, 199, 183, 0.2);
        border-radius: 0.75rem;
        color: #bff7ed;
        font-size: 0.78rem;
        background: rgba(40, 199, 183, 0.08);
    }

    .cp-status-dot {
        width: 0.52rem;
        height: 0.52rem;
        border-radius: 999px;
        background: #37ddbd;
        box-shadow: 0 0 0 4px rgba(55, 221, 189, 0.1);
    }

    .cp-section-label {
        margin: 1.25rem 0 0.45rem;
        color: #71839d;
        font-size: 0.7rem;
        font-weight: 750;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }

    .cp-header {
        display: block;
        margin-bottom: 0.8rem;
        padding-bottom: 0.85rem;
        border-bottom: 1px solid var(--cp-border);
    }

    .cp-eyebrow {
        margin-bottom: 0.35rem;
        color: #8d82ff;
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.13em;
        text-transform: uppercase;
    }

    .cp-title {
        margin: 0 !important;
        padding: 0 !important;
        color: var(--cp-text);
        font-size: clamp(1.65rem, 3vw, 2.15rem);
        font-weight: 780;
        letter-spacing: -0.045em;
        line-height: 1.05;
    }

    .cp-subtitle {
        margin-top: 0.55rem;
        color: var(--cp-muted);
        font-size: 0.93rem;
    }

    .cp-badges {
        display: flex;
        flex-wrap: wrap;
        justify-content: flex-start;
        gap: 0.5rem;
        margin-top: 0.7rem;
    }

    .cp-badge {
        white-space: nowrap;
        padding: 0.48rem 0.7rem;
        border: 1px solid var(--cp-border);
        border-radius: 999px;
        color: #bac8db;
        font-size: 0.72rem;
        background: rgba(16, 29, 48, 0.72);
    }

    .cp-chat-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: 0.9rem;
        padding: 0.1rem 0 0.8rem;
        border-bottom: 1px solid var(--cp-border);
    }

    .cp-chat-title {
        margin: 0 !important;
        padding: 0 !important;
        color: var(--cp-text);
        font-size: 1.1rem;
        font-weight: 720;
        letter-spacing: -0.02em;
    }

    .cp-chat-meta {
        color: var(--cp-muted);
        font-size: 0.74rem;
        white-space: nowrap;
    }

    .cp-empty {
        margin-top: 1.1rem;
        padding: clamp(1.7rem, 4vw, 2.4rem);
        border: 1px solid var(--cp-border);
        border-radius: 1.5rem;
        text-align: center;
        background:
            linear-gradient(145deg, rgba(23, 39, 64, 0.78), rgba(12, 24, 41, 0.72));
        box-shadow: 0 28px 70px rgba(0, 0, 0, 0.22);
    }

    .cp-empty-icon {
        display: grid;
        width: 3.6rem;
        height: 3.6rem;
        margin: 0 auto 0.85rem;
        place-items: center;
        border: 1px solid rgba(255, 255, 255, 0.16);
        border-radius: 1.25rem;
        color: white;
        font-size: 1.55rem;
        background: linear-gradient(135deg, var(--cp-accent), var(--cp-accent-two));
        box-shadow: 0 18px 44px rgba(80, 97, 224, 0.3);
    }

    .cp-empty h2 {
        margin: 0 !important;
        padding: 0 !important;
        color: var(--cp-text);
        font-size: 1.55rem;
        letter-spacing: -0.03em;
    }

    .cp-empty p {
        max-width: 35rem;
        margin: 0.55rem auto 1rem;
        color: var(--cp-muted);
        line-height: 1.5;
    }

    .cp-prompts {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.7rem;
        text-align: left;
    }

    .cp-prompt-card {
        padding: 0.85rem;
        border: 1px solid var(--cp-border);
        border-radius: 0.8rem;
        color: #b9c8dc;
        font-size: 0.78rem;
        background: rgba(8, 18, 32, 0.4);
    }

    [data-testid="stChatMessage"] {
        margin-bottom: 0.7rem;
        padding: 1rem 1.1rem;
        border: 1px solid var(--cp-border);
        border-radius: 1rem;
        background: rgba(15, 29, 48, 0.74);
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
    }

    [data-testid="stChatMessage"] p {
        color: #e8eef8 !important;
        line-height: 1.68;
    }

    [data-testid="stChatMessage"] code,
    [data-testid="stChatMessage"] li,
    [data-testid="stChatMessage"] strong {
        color: #e8eef8 !important;
    }

    [data-testid="stBottom"] {
        border-top: 1px solid var(--cp-border);
        background: rgba(7, 17, 31, 0.96) !important;
        backdrop-filter: blur(18px);
    }

    [data-testid="stChatInput"] {
        border: 1px solid rgba(124, 108, 255, 0.3);
        border-radius: 1rem;
        background: #111c2f !important;
        box-shadow: 0 18px 50px rgba(0, 0, 0, 0.28);
    }

    [data-testid="stChatInput"] textarea {
        color: #e8eef8 !important;
        background: transparent !important;
        caret-color: #9b91ff;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: #8291a8 !important;
    }

    .stButton > button {
        min-height: 2.45rem;
        border: 1px solid var(--cp-border);
        border-radius: 0.7rem;
        color: #d8e4f3;
        background: rgba(18, 32, 52, 0.72);
        transition: border-color 160ms ease, background 160ms ease, transform 160ms ease;
    }

    .stButton > button:hover {
        border-color: rgba(124, 108, 255, 0.65);
        color: white;
        background: rgba(52, 48, 105, 0.55);
        transform: translateY(-1px);
    }

    .st-key-new_conversation button {
        border-color: transparent;
        color: white;
        font-weight: 700;
        background: linear-gradient(135deg, #6c5ce7, #4e8df5);
        box-shadow: 0 12px 28px rgba(80, 85, 220, 0.24);
    }

    [data-baseweb="select"] > div {
        border-color: var(--cp-border);
        color: #e8eef8 !important;
        background: #111c2f !important;
    }

    [data-baseweb="select"] span,
    [data-baseweb="select"] input {
        color: #e8eef8 !important;
    }

    hr {
        border-color: var(--cp-border) !important;
    }

    @media (max-width: 720px) {
        .cp-prompts {
            grid-template-columns: 1fr;
        }
    }
</style>
"""


def _initialize_session() -> None:
    st.session_state.setdefault("conversation_id", None)
    st.session_state.setdefault("messages", [])


def _load_conversation(conversation_id: str) -> bool:
    conversation = get_conversation(conversation_id)
    if conversation is None:
        return False

    st.session_state.conversation_id = conversation_id
    st.session_state.messages = conversation.get("messages", [])
    return True


def _start_new_conversation() -> None:
    st.session_state.conversation_id = None
    st.session_state.messages = []


def _build_prompt(messages: list[dict[str, Any]]) -> str:
    transcript = "\n".join(
        f"{message.get('role', 'user').capitalize()}: "
        f"{message.get('content', '')}"
        for message in messages
    )

    return (
        "You are a helpful, accurate, and concise AI assistant. Continue "
        "the conversation below. Respond only as the assistant.\n\n"
        f"{transcript}\nAssistant:"
    )


def _render_empty_state() -> None:
    st.markdown(
        """
        <section class="cp-empty">
            <div class="cp-empty-icon">✦</div>
            <h2>What can we explore today?</h2>
            <p>
                Your conversations stay on this machine. Choose a local model,
                ask anything, and ConvoPro will keep your history organized.
            </p>
            <div class="cp-prompts">
                <div class="cp-prompt-card">✎ Draft and improve your writing</div>
                <div class="cp-prompt-card">⌘ Explain code and debug issues</div>
                <div class="cp-prompt-card">◎ Brainstorm ideas and plans</div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
_initialize_session()

try:
    installed_models = get_models_list()
except Exception as exc:
    st.error(
        "Could not connect to Ollama. Make sure the Docker container is "
        f"running. Details: {exc}"
    )
    st.stop()

if not installed_models:
    st.warning("No Ollama models are installed. Pull a model before chatting.")
    st.code("docker compose exec ollama ollama pull gemma2:2b")
    st.stop()

try:
    saved_conversations = get_all_conversations()
except Exception as exc:
    st.error(f"Could not load conversations from MongoDB: {exc}")
    saved_conversations = {}

with st.sidebar:
    st.markdown(
        """
        <div class="cp-brand">
            <div class="cp-brand-mark">✦</div>
            <div>
                <div class="cp-brand-name">ConvoPro</div>
                <div class="cp-brand-subtitle">Private local intelligence</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "＋  New conversation",
        key="new_conversation",
        use_container_width=True,
    ):
        _start_new_conversation()
        st.rerun()

    st.markdown('<div class="cp-section-label">Local model</div>', unsafe_allow_html=True)
    selected_model = st.selectbox(
        "Local model",
        installed_models,
        label_visibility="collapsed",
        key="selected_model",
    )
    st.markdown(
        f"""
        <div class="cp-status">
            <span class="cp-status-dot"></span>
            <span>{escape(selected_model)} is ready</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="cp-section-label">Recent chats · {len(saved_conversations)}</div>',
        unsafe_allow_html=True,
    )

    if not saved_conversations:
        st.caption("Your saved conversations will appear here.")

    for conversation_id, title in saved_conversations.items():
        is_active = conversation_id == st.session_state.conversation_id
        button_label = f"●  {title}" if is_active else title

        if st.button(
            button_label,
            key=f"conversation-{conversation_id}",
            type="primary" if is_active else "secondary",
            use_container_width=True,
        ):
            if _load_conversation(conversation_id):
                st.rerun()
            else:
                st.error("The selected conversation no longer exists.")

    st.markdown('<div class="cp-section-label">Privacy</div>', unsafe_allow_html=True)
    st.caption("🔒 Ollama and MongoDB run locally on your computer.")

safe_model_name = escape(selected_model)
if st.session_state.messages:
    active_title = saved_conversations.get(
        st.session_state.conversation_id,
        "Current conversation",
    )
    st.markdown(
        f"""
        <header class="cp-chat-header">
            <h1 class="cp-chat-title">{escape(active_title)}</h1>
            <div class="cp-chat-meta">◉ {safe_model_name} · saved locally</div>
        </header>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f"""
        <header class="cp-header">
            <div class="cp-eyebrow">Local-first AI workspace</div>
            <h1 class="cp-title">Your private thinking partner.</h1>
            <div class="cp-subtitle">Fast, focused conversations without sending data to the cloud.</div>
            <div class="cp-badges">
                <span class="cp-badge">◉ {safe_model_name}</span>
                <span class="cp-badge">MongoDB history</span>
                <span class="cp-badge">100% local</span>
            </div>
        </header>
        """,
        unsafe_allow_html=True,
    )

if not st.session_state.messages:
    _render_empty_state()
else:
    for message in st.session_state.messages:
        role = message.get("role", "assistant")
        if role not in {"user", "assistant"}:
            role = "assistant"

        with st.chat_message(role):
            st.markdown(message.get("content", ""))

if user_message := st.chat_input(f"Message {selected_model}"):
    user_entry = {"role": "user", "content": user_message}

    if st.session_state.conversation_id is None:
        with st.spinner("Creating your conversation..."):
            title = get_title(user_message, selected_model)
        conversation_id = create_new_conversation(
            title=title,
            role="user",
            content=user_message,
        )
        st.session_state.conversation_id = conversation_id
    else:
        conversation_id = st.session_state.conversation_id
        if not add_message(conversation_id, "user", user_message):
            st.error("Could not save the message because the conversation is missing.")
            st.stop()

    st.session_state.messages.append(user_entry)

    with st.chat_message("user"):
        st.markdown(user_message)

    try:
        llm = get_ollama_llm(selected_model)
        with st.chat_message("assistant"):
            with st.spinner(f"{selected_model} is thinking..."):
                assistant_message = llm.invoke(
                    _build_prompt(st.session_state.messages)
                ).strip()
            st.markdown(assistant_message)
    except Exception as exc:
        st.error(f"Ollama could not generate a response: {exc}")
        st.stop()

    if not assistant_message:
        st.warning("The model returned an empty response. Please try again.")
        st.stop()

    if not add_message(conversation_id, "assistant", assistant_message):
        st.error("The response was generated but could not be saved to MongoDB.")
        st.stop()

    st.session_state.messages.append(
        {"role": "assistant", "content": assistant_message}
    )
    st.rerun()
