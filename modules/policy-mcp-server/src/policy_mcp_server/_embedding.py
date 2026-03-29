"""OpenAI-compatible embedding client.

Reads configuration from environment variables:
  EMBEDDING_BASE_URL  — API base URL (e.g. http://localhost:11434/v1)
  EMBEDDING_API_KEY   — API key (default: "no-key" for self-hosted)
  EMBEDDING_MODEL     — Model name (e.g. nomic-embed-text)
"""

import logging
import os

from policy_mcp_server.exceptions import SearchError

logger = logging.getLogger("policy-mcp-server")

_client = None


def is_embedding_configured() -> bool:
    return bool(os.environ.get("EMBEDDING_BASE_URL")) and bool(
        os.environ.get("EMBEDDING_MODEL")
    )


def _get_client():
    global _client
    if _client is not None:
        return _client

    base_url = os.environ.get("EMBEDDING_BASE_URL")
    if not base_url:
        raise SearchError(
            "EMBEDDING_BASE_URL is not set. "
            "Configure it to enable vector indexing and semantic search."
        )

    api_key = os.environ.get("EMBEDDING_API_KEY", "no-key")

    from openai import OpenAI

    _client = OpenAI(base_url=base_url, api_key=api_key)
    logger.info("Embedding client initialised (base_url=%s)", base_url)
    return _client


def _get_model() -> str:
    model = os.environ.get("EMBEDDING_MODEL", "")
    if not model:
        raise SearchError(
            "EMBEDDING_MODEL is not set. "
            "Configure it to specify which embedding model to use."
        )
    return model


def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of texts.

    Returns a list of float vectors, one per input text.
    """
    client = _get_client()
    model = _get_model()

    response = client.embeddings.create(input=texts, model=model)
    return [item.embedding for item in response.data]


def get_embedding_dimension() -> int:
    """Probe the embedding dimension by generating a single test embedding."""
    vecs = get_embeddings(["dimension probe"])
    return len(vecs[0])
