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

1. LlamaIndex reads every PDF in `data/` and builds a searchable index of the text.
2. For each question, it pulls the most relevant passages from the papers.
3. An OpenAI model writes the answer from those passages and remembers the conversation.

The interface is built with Streamlit's chat elements.

## Run it yourself

1. Get an OpenAI API key at https://platform.openai.com/account/api-keys.
2. Install the requirements:
   ```
   pip install -r requirements.txt
   ```
3. Create `.streamlit/secrets.toml` with your key:
   ```
   openai_key = "sk-..."
   ```
   To use a different model than `gpt-4o-mini`, add `openai_model = "..."` on the next line.
4. Start the app:
   ```
   streamlit run streamlit_app.py
   ```

The first start indexes all the papers and takes a few minutes.

## Tools

Python, Streamlit, LlamaIndex, OpenAI
