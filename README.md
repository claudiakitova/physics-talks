# PhysicsTalks ☢️

A chatbot that answers condensed matter physics questions from a library of about 40 scientific papers and books.

Ask something like "What drives orbital ordering in KCuF3?" and it finds the relevant passages in the papers and answers from them.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://physics-talks.streamlit.app/)

## The library

The PDFs in [data/](data/) cover:

- Orbital ordering and the Jahn-Teller effect (KCuF3, K2CuF4, and related fluorides)
- Multiferroics and magnetoelectrics
- Transition-metal oxides and strongly correlated electrons
- Soft magnetic materials and oxide spintronics
- Superconductor-insulator transitions, time crystals, and phase transformations

It includes D. Khomskii's *Transition Metal Compounds* and G. Nénert's thesis *Orbital Ordering and Multiferroics*.

## How it works

1. The papers are split into passages and indexed for search with a small free model that runs inside the app. The index is saved in [storage/](storage/), so the app starts in seconds.
2. For each question, the app finds the most relevant passages.
3. Google Gemini writes the answer from those passages and remembers the conversation.

The interface is built with Streamlit's chat elements.

## Run it yourself

1. Get a free Gemini API key at https://aistudio.google.com/apikey.
2. Install the requirements:
   ```
   pip install -r requirements.txt
   ```
3. Create `.streamlit/secrets.toml` with your key:
   ```
   gemini_key = "..."
   ```
   To use a different model than `gemini-3.5-flash-lite`, add `gemini_model = "..."` on the next line.
4. Start the app:
   ```
   streamlit run streamlit_app.py
   ```

After adding or removing papers in `data/`, rebuild the index with `python build_index.py`.

## Tools

Python, Streamlit, LlamaIndex, Google Gemini, FastEmbed
