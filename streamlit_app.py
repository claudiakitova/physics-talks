import streamlit as st
from llama_index.core import Settings, StorageContext, load_index_from_storage
from llama_index.llms.google_genai import GoogleGenAI

from local_embedding import LocalEmbedding

st.set_page_config(page_title="PhysicsTalks", page_icon="☢️", layout="centered")
st.title("PhysicsTalks ☢️")

try:
    api_key = st.secrets["gemini_key"]
except Exception:  # no secrets file, or the key is missing
    api_key = None
if not api_key:
    st.error("Add your Gemini API key to the app's secrets as `gemini_key`.")
    st.stop()

SYSTEM_PROMPT = (
    "You are an expert in condensed matter physics. Answer scientific and technical "
    "questions using the papers in the library. Keep your answers technical and based "
    "on facts. If the papers don't cover something, say so instead of guessing."
)

try:
    model = st.secrets["gemini_model"]
except Exception:
    model = "gemini-3.5-flash-lite"

Settings.llm = GoogleGenAI(model=model, api_key=api_key, temperature=0.5)


@st.cache_resource(show_spinner=False)
def load_index():
    with st.spinner("Loading the papers..."):
        Settings.embed_model = LocalEmbedding()
        return load_index_from_storage(StorageContext.from_defaults(persist_dir="./storage"))


index = load_index()

if "chat_engine" not in st.session_state:
    st.session_state.chat_engine = index.as_chat_engine(
        chat_mode="condense_plus_context", system_prompt=SYSTEM_PROMPT
    )

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hey! Ask me a question."}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt := st.chat_input("Your question"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = st.session_state.chat_engine.chat(prompt).response
        st.write(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
