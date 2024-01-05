from urllib.parse import urljoin

import requests
from langchain_core.embeddings import Embeddings
from pydantic import BaseModel


class HuggingfaceTEIEmbeddings(BaseModel, Embeddings):
    """See <https://huggingface.github.io/text-embeddings-inference/>"""

    base_url: str
    normalize: bool = True
    truncate: bool = False
    query_instruction: str
    """Instruction to use for embedding query."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        response = requests.post(
            urljoin(self.base_url, "/embed"),
            json={
                "inputs": texts,
                "normalize": self.normalize,
                "truncate": self.truncate,
            },
        )
        return response.json()

    def embed_query(self, text: str) -> list[float]:
        instructed_query = self.query_instruction + text
        return self.embed_documents([instructed_query])[0]
