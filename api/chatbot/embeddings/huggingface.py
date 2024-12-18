from __future__ import annotations

import asyncio
import itertools
import json
from sys import version_info
from typing import Any, Self, TypeVar, TYPE_CHECKING
from urllib.parse import urljoin

from huggingface_hub import AsyncInferenceClient, InferenceClient
from langchain_core.documents import Document
from langchain_core.documents.compressor import BaseDocumentCompressor
from langchain_core.embeddings import Embeddings
from pydantic import BaseModel, model_validator

if version_info >= (3, 12):
    from typing import override
else:

    def override(func):
        return func


if TYPE_CHECKING:
    from collections.abc import Sequence

    from langchain_core.callbacks import Callbacks


T = TypeVar("T")


class BaseHuggingfaceTEI(BaseModel):
    base_url: str
    batch_size: int = 32
    """client batch size. text-embedding-inference defaults to 32."""
    timeout: int = 120
    client: Any = None  #: :meta private:
    async_client: Any = None  #: :meta private:

    @property
    def model(self) -> str:
        raise NotImplementedError(
            "Must implement the `model` property, usually `urljoin(self.base_url, 'your server path')`"
        )

    @model_validator(mode="after")
    def validate_environment(self) -> Self:
        """Validate that huggingface_hub python package exists in environment."""
        self.client = InferenceClient(
            model=self.model,
            timeout=self.timeout,
        )
        self.async_client = AsyncInferenceClient(
            model=self.model,
            timeout=self.timeout,
        )
        return self

    def _split_inputs(self, inputs: Sequence[T]) -> list[list[T]]:
        """Split documents into chunks of size `self.batch_size`."""
        return [
            inputs[i : i + self.batch_size]
            for i in range(0, len(inputs), self.batch_size)
        ]


class HuggingfaceTEIEmbeddings(BaseHuggingfaceTEI, Embeddings):
    """Embeddings using Huggingface's text-embeddings-inference service.
    See <https://huggingface.github.io/text-embeddings-inference/>
    """

    normalize: bool = True
    truncate: bool = False

    @property
    def model(self) -> str:
        return urljoin(self.base_url, "/embed")

    @override
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        texts_chunks = self._split_inputs(texts)
        responses = []
        for chunk in texts_chunks:
            responses += self._embed(chunk)
        return responses

    @override
    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        """Asynchronous Embed search docs."""
        texts_chunks = self._split_inputs(texts)
        tasks = [self._aembed(inputs=chunk) for chunk in texts_chunks]

        res = await asyncio.gather(*tasks)
        return list(itertools.chain.from_iterable(res))

    @override
    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]

    @override
    async def aembed_query(self, text: str) -> list[float]:
        embeddings = await self.aembed_documents([text])
        return embeddings[0]

    def _embed(self, inputs: list[str]) -> list[float]:
        responses = self.client.post(
            json={
                "inputs": inputs,
                "normalize": self.normalize,
                "truncate": self.truncate,
            }
        )
        return json.loads(responses.decode())

    async def _aembed(self, inputs: list[str]) -> list[float]:
        """Asynchronous POST request."""
        responses = await self.async_client.post(
            json={
                "inputs": inputs,
                "normalize": self.normalize,
                "truncate": self.truncate,
            }
        )
        return json.loads(responses.decode())


class RerankResponseEntry(BaseModel):
    """Rerank response entry."""

    index: int
    score: float


class HuggingfaceTEIReranker(BaseHuggingfaceTEI, BaseDocumentCompressor):
    """Document compressor using Flashrank interface."""

    score_threshold: float | None = None

    @property
    def model(self) -> str:
        return urljoin(self.base_url, "/rerank")

    @override
    def compress_documents(
        self,
        documents: Sequence[Document],
        query: str,
        callbacks: Callbacks | None = None,  # noqa: ARG002
    ) -> Sequence[Document]:
        docs_chunks = self._split_inputs(documents)
        responses = []
        for chunk in docs_chunks:
            idxed_documents = {
                i: doc for i, doc in enumerate(chunk) if doc.page_content
            }

            res = self._rerank(
                query, [doc.page_content for doc in idxed_documents.values()]
            )
            if self.score_threshold is not None:
                res = filter(lambda x: x["score"] >= self.score_threshold, res)

            for r in res:
                original_doc = idxed_documents[r["index"]]
                doc = Document(
                    page_content=original_doc.page_content,
                    metadata={"relevance_score": r["score"]} | original_doc.metadata,
                )
                responses.append(doc)
        return responses

    @override
    async def acompress_documents(
        self,
        documents: Sequence[Document],
        query: str,
        callbacks: Callbacks | None = None,  # noqa: ARG002
    ) -> Sequence[Document]:
        docs_chunks = self._split_inputs(documents)
        responses = []
        for chunk in docs_chunks:
            idxed_documents = {
                i: doc for i, doc in enumerate(chunk) if doc.page_content
            }

            res = await self._arerank(
                query, [doc.page_content for doc in idxed_documents.values()]
            )
            if self.score_threshold is not None:
                res = filter(lambda x: x["score"] >= self.score_threshold, res)

            for r in res:
                original_doc = idxed_documents[r["index"]]
                doc = Document(
                    page_content=original_doc.page_content,
                    metadata={"relevance_score": r["score"]} | original_doc.metadata,
                )
                responses.append(doc)
        return responses

    def _rerank(self, query: str, inputs: list[str]) -> list[RerankResponseEntry]:
        responses = self.client.post(
            json={
                "query": query,
                "texts": inputs,
            },
        )
        return json.loads(responses.decode())

    async def _arerank(
        self, query: str, inputs: list[str]
    ) -> list[RerankResponseEntry]:
        """Asynchronous POST request."""
        responses = await self.async_client.post(
            json={
                "query": query,
                "texts": inputs,
            },
        )
        return json.loads(responses.decode())
