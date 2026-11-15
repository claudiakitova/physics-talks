"""Build the search index of the papers in data/ and save it to storage/.

Run this again after adding or removing papers:
    python build_index.py
"""
from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex

from local_embedding import LocalEmbedding

Settings.embed_model = LocalEmbedding()

docs = SimpleDirectoryReader("./data", required_exts=[".pdf"], recursive=True).load_data()
index = VectorStoreIndex.from_documents(docs, show_progress=True)
index.storage_context.persist("./storage")
print(f"Indexed {len(docs)} pages into storage/")
