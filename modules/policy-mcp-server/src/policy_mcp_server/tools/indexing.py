"""Vector indexing tool — embeds section content and stores in Milvus."""

import logging
import os
from pathlib import Path

from policy_mcp_server._embedding import (
    get_embedding_dimension,
    get_embeddings,
    is_embedding_configured,
)
from policy_mcp_server._path_utils import _resolve_task_path
from policy_mcp_server.exceptions import SearchError, WorkspaceError

logger = logging.getLogger("policy-mcp-server")

COLLECTION_PREFIX = "policy_"


def _get_collection_name(task_id: str) -> str:
    safe_id = task_id.replace("-", "_")
    return f"{COLLECTION_PREFIX}{safe_id}"


def delete_index(task_id: str) -> dict[str, str]:
    """Delete the Milvus collection for a task if it exists."""
    milvus_uri = os.environ.get("MILVUS_URI")
    if not milvus_uri:
        raise SearchError(
            "MILVUS_URI is not set. Cannot clean vector index without a Milvus connection."
        )

    collection_name = _get_collection_name(task_id)
    try:
        from pymilvus import MilvusClient

        client = MilvusClient(uri=milvus_uri)
        if client.has_collection(collection_name):
            client.drop_collection(collection_name)
            logger.info("Dropped collection '%s'", collection_name)
            return {"status": "deleted", "detail": f"Collection '{collection_name}' deleted"}
        return {"status": "not_found", "detail": f"Collection '{collection_name}' does not exist"}
    except Exception as exc:
        raise SearchError(f"Milvus cleanup failed: {exc}") from exc


def index_sections(task_id: str) -> str:
    """Read all sections from a task workspace, embed them, and index into Milvus.

    Creates (or recreates) a Milvus collection named ``policy_{task_id}``
    containing each section's text and its embedding vector.
    """
    if not is_embedding_configured():
        raise SearchError(
            "Embedding is not configured. "
            "Set EMBEDDING_BASE_URL and EMBEDDING_MODEL environment variables."
        )

    milvus_uri = os.environ.get("MILVUS_URI")
    if not milvus_uri:
        raise SearchError(
            "MILVUS_URI is not set. Cannot index without a Milvus connection."
        )

    try:
        sections_dir = _resolve_task_path(task_id, "sections")
    except WorkspaceError as exc:
        raise SearchError(f"Cannot index: {exc}") from exc

    if not sections_dir.is_dir():
        raise SearchError(
            f"No sections directory found for task '{task_id}'. "
            "Run document ingestion first."
        )

    md_files = sorted(
        f for f in sections_dir.glob("*.md") if f.stem != "_index"
    )
    if not md_files:
        raise SearchError(
            f"No section files found in task '{task_id}/sections/'. "
            "Run document ingestion first."
        )

    section_ids: list[str] = []
    section_texts: list[str] = []
    for md_file in md_files:
        content = md_file.read_text(encoding="utf-8").strip()
        if content:
            section_ids.append(md_file.stem)
            section_texts.append(content)

    if not section_texts:
        raise SearchError("All section files are empty — nothing to index.")

    logger.info(
        "Indexing %d sections for task '%s'", len(section_texts), task_id
    )

    try:
        dimension = get_embedding_dimension()
    except Exception as exc:
        raise SearchError(
            f"Failed to connect to Embedding API: {exc}"
        ) from exc

    try:
        embeddings = get_embeddings(section_texts)
    except Exception as exc:
        raise SearchError(
            f"Embedding API call failed: {exc}"
        ) from exc

    collection_name = _get_collection_name(task_id)

    try:
        from pymilvus import CollectionSchema, DataType, FieldSchema, MilvusClient

        client = MilvusClient(uri=milvus_uri)

        if client.has_collection(collection_name):
            logger.info("Dropping existing collection '%s'", collection_name)
            client.drop_collection(collection_name)

        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="section_id", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dimension),
        ]
        schema = CollectionSchema(fields=fields)

        client.create_collection(
            collection_name=collection_name,
            schema=schema,
        )

        data = [
            {"section_id": sid, "text": txt, "embedding": emb}
            for sid, txt, emb in zip(section_ids, section_texts, embeddings)
        ]
        client.insert(collection_name=collection_name, data=data)

        index_params = client.prepare_index_params()
        index_params.add_index(
            field_name="embedding",
            index_type="IVF_FLAT",
            metric_type="COSINE",
            params={"nlist": 128},
        )
        client.create_index(
            collection_name=collection_name,
            index_params=index_params,
        )

        client.load_collection(collection_name)

    except Exception as exc:
        raise SearchError(
            f"Milvus operation failed: {exc}"
        ) from exc

    summary = (
        f"Indexed {len(section_texts)} sections into Milvus collection '{collection_name}'.\n"
        f"Embedding dimension: {dimension}\n"
        f"Sections: {', '.join(section_ids)}"
    )
    logger.info(summary)
    return summary
