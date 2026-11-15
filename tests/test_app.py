"""Run the app without a real Gemini key and check that it loads and answers.

    python tests/test_app.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

import llama_index.llms.google_genai as google_genai  # noqa: E402
from llama_index.core.llms import MockLLM  # noqa: E402

google_genai.GoogleGenAI = lambda **kwargs: MockLLM(max_tokens=10)

from streamlit.testing.v1 import AppTest  # noqa: E402

APP = os.path.join(ROOT, "streamlit_app.py")

# 1. With a key: the app loads the library and answers a question.
at = AppTest.from_file(APP, default_timeout=600)
at.secrets["gemini_key"] = "test"
at.run()
assert not at.exception, f"App crashed on start: {at.exception}"

at.chat_input[0].set_value("What drives orbital ordering in KCuF3?").run()
assert not at.exception, f"App crashed on a question: {at.exception}"
roles = [m.name for m in at.chat_message]
assert roles[-2:] == ["user", "assistant"], f"No answer shown: {roles}"
sources = [e.label for e in at.expander]
assert any(label.startswith("Sources") for label in sources), "No sources shown"

# 2. Without a key: the app explains what to do instead of crashing.
at = AppTest.from_file(APP)
at.run()
assert at.error and "gemini_key" in at.error[0].value, "Missing-key message not shown"

print("All checks passed")
