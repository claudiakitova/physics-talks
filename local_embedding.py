"""Free, local text embeddings for searching the papers (no API key needed)."""
from typing import List

from fastembed import TextEmbedding
from llama_index.core.embeddings import BaseEmbedding
from pydantic import PrivateAttr

MODEL_NAME = "BAAI/bge-small-en-v1.5"


class LocalEmbedding(BaseEmbedding):
    _model: TextEmbedding = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(model_name=MODEL_NAME, **kwargs)
        self._model = TextEmbedding(model_name=MODEL_NAME)

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        return [vector.tolist() for vector in self._model.embed(texts)]

    def _get_text_embedding(self, text: str) -> List[float]:
        return self._get_text_embeddings([text])[0]

    def _get_query_embedding(self, query: str) -> List[float]:
        return next(self._model.query_embed(query)).tolist()

    async def _aget_query_embedding(self, query: str) -> List[float]:
        return self._get_query_embedding(query)
