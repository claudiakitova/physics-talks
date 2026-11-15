from pathlib import Path

import streamlit as st
from llama_index.core import Settings, StorageContext, load_index_from_storage
from llama_index.llms.google_genai import GoogleGenAI

from local_embedding import LocalEmbedding

st.set_page_config(page_title="PhysicsTalks", page_icon="⚛️", layout="centered")

BOT, USER = "⚛️", "🧑‍🔬"
GREETING = "Ask me anything about the papers in the library."
EXAMPLES = [
    "What drives orbital ordering in KCuF3?",
    "Why are multiferroics so rare?",
    "Explain the Jahn-Teller effect simply",
    "What is a time crystal?",
]
TOPICS = [
    "Orbital ordering and the Jahn-Teller effect",
    "Multiferroics and magnetoelectrics",
    "Transition-metal oxides and correlated electrons",
    "Soft magnets and oxide spintronics",
    "Superconductor-insulator transitions",
    "Time crystals and phase transformations",
]
SYSTEM_PROMPT = (
    "You are an expert in condensed matter physics. Answer questions using the papers "
    "in the library. Be technical, precise, and based on facts. Get straight to the "
    "answer: don't greet the user and don't talk about your 'context' or 'documents'. "
    "When useful, mention which paper a point comes from. Use LaTeX between $ signs for "
    "formulas. If the papers don't cover something, say so instead of guessing."
)

st.markdown(
    """
    <style>
    .block-container {padding-top: 2.5rem; max-width: 760px;}
    .subtitle {color: #9AA4B8; font-size: 1.05rem; margin-top: -0.8rem; margin-bottom: 1.5rem;}
    div[data-testid="stButton"] button {
        width: 100%; text-align: left; border-radius: 12px;
        border: 1px solid #26304A; background: #151C30;
    }
    div[data-testid="stButton"] button:hover {border-color: #4FC3F7; color: #4FC3F7;}
    .source {color: #9AA4B8; font-size: 0.9rem; line-height: 1.6;}
    </style>
    """,
    unsafe_allow_html=True,
)

try:
    api_key = st.secrets["gemini_key"]
except Exception:  # no secrets file, or the key is missing
    api_key = None

try:
    model = st.secrets["gemini_model"]
except Exception:
    model = "gemini-3.5-flash-lite"


def paper_name(file_name):
    return file_name.removesuffix(".pdf").replace("_", " ")


def source_list(nodes):
    seen, lines = set(), []
    for node in nodes:
        name = paper_name(node.metadata.get("file_name", "Unknown"))
        page = node.metadata.get("page_label")
        key = (name, page)
        if key not in seen:
            seen.add(key)
            lines.append(f"{name}, p. {page}" if page else name)
    return lines


def show_message(message):
    with st.chat_message(message["role"], avatar=BOT if message["role"] == "assistant" else USER):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander(f"Sources ({len(message['sources'])})"):
                st.markdown(
                    "<div class='source'>" + "<br>".join(message["sources"]) + "</div>",
                    unsafe_allow_html=True,
                )


def reset_chat():
    st.session_state.messages = [{"role": "assistant", "content": GREETING}]
    st.session_state.pop("chat_engine", None)


with st.sidebar:
    st.markdown("### ⚛️ PhysicsTalks")
    paper_count = len(list(Path("data").glob("*.pdf")))
    st.caption(f"Answers come from {paper_count} papers and books on condensed matter physics.")
    st.markdown("**In the library**")
    st.markdown("\n".join(f"- {t}" for t in TOPICS))
    st.button("New chat", on_click=reset_chat, use_container_width=True)

st.title("PhysicsTalks")
st.markdown(
    "<div class='subtitle'>A research assistant for condensed matter physics, "
    "answering from a library of scientific papers.</div>",
    unsafe_allow_html=True,
)

if not api_key:
    st.error("Add your Gemini API key to the app's secrets as `gemini_key`.")
    st.stop()

Settings.llm = GoogleGenAI(model=model, api_key=api_key, temperature=0.3)


@st.cache_resource(show_spinner=False)
def load_index():
    with st.spinner("Loading the library..."):
        Settings.embed_model = LocalEmbedding()
        return load_index_from_storage(StorageContext.from_defaults(persist_dir="./storage"))


index = load_index()

if "messages" not in st.session_state:
    reset_chat()
if "chat_engine" not in st.session_state:
    st.session_state.chat_engine = index.as_chat_engine(
        chat_mode="condense_plus_context", system_prompt=SYSTEM_PROMPT
    )

for message in st.session_state.messages:
    show_message(message)

prompt = None
if len(st.session_state.messages) == 1:
    cols = st.columns(2)
    for i, example in enumerate(EXAMPLES):
        if cols[i % 2].button(example, key=f"example_{i}"):
            prompt = example

typed = st.chat_input("Ask a physics question")
prompt = typed or prompt

if prompt:
    user_message = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_message)
    show_message(user_message)
    with st.chat_message("assistant", avatar=BOT):
        with st.spinner("Searching the papers..."):
            response = st.session_state.chat_engine.chat(prompt)
    answer = {
        "role": "assistant",
        "content": response.response,
        "sources": source_list(response.source_nodes),
    }
    st.session_state.messages.append(answer)
    st.rerun()
