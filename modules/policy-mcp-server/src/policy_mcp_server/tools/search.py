import logging
import os
import re
from pathlib import Path

from policy_mcp_server._path_utils import _resolve_task_path
from policy_mcp_server.exceptions import SearchError, WorkspaceError

logger = logging.getLogger("policy-mcp-server")

CONTEXT_CHARS = 150
MAX_TEXT_RESULTS = 20
MAX_VECTOR_RESULTS = 10


def search_content(task_id: str, query: str) -> str:
    """Search across all sections of a task using full-text and vector search.

    Combines results from both methods, deduplicates by section, and returns
    matched snippets with their source section IDs.
    """
    text_results = _fulltext_search(task_id, query)
    vector_results = _vector_search(task_id, query)

    merged = _merge_results(text_results, vector_results)

    if not merged:
        return f"No results found for query: '{query}'"

    lines = [f"## Search results for: '{query}'\n"]
    for item in merged:
        lines.append(f"### Section: {item['section_id']} (source: {item['source']})")
        lines.append(f"{item['snippet']}\n")
    return "\n".join(lines)


def _fulltext_search(task_id: str, query: str) -> list[dict]:
    """Grep-like full-text search across all section Markdown files."""
    try:
        sections_dir = _resolve_task_path(task_id, "sections")
    except WorkspaceError:
        return []

    if not sections_dir.is_dir():
        return []

    results: list[dict] = []
    pattern = re.compile(re.escape(query), re.IGNORECASE)

    for md_file in sorted(sections_dir.glob("*.md")):
        if md_file.stem == "_index":
            continue
        content = md_file.read_text(encoding="utf-8")
        for match in pattern.finditer(content):
            start = max(0, match.start() - CONTEXT_CHARS)
            end = min(len(content), match.end() + CONTEXT_CHARS)
            snippet = content[start:end].strip()
            if start > 0:
                snippet = f"...{snippet}"
            if end < len(content):
                snippet = f"{snippet}..."

            results.append({
                "section_id": md_file.stem,
                "snippet": snippet,
                "source": "fulltext",
            })
            if len(results) >= MAX_TEXT_RESULTS:
                return results
    return results


def _vector_search(task_id: str, query: str) -> list[dict]:
    """Semantic vector search via Milvus.

    Embeds the query using the configured Embedding API, then searches
    the task's Milvus collection for similar section chunks.
    Falls back gracefully if Milvus or Embedding is not available.
    """
    milvus_uri = os.environ.get("MILVUS_URI")
    if not milvus_uri:
        return []

    from policy_mcp_server._embedding import is_embedding_configured

    if not is_embedding_configured():
        logger.info("Embedding not configured, skipping vector search")
        return []

    try:
        from pymilvus import MilvusClient

        from policy_mcp_server._embedding import get_embeddings
        from policy_mcp_server.tools.indexing import _get_collection_name

        client = MilvusClient(uri=milvus_uri)
        collection_name = _get_collection_name(task_id)

        if not client.has_collection(collection_name):
            logger.info("Milvus collection '%s' not found, skipping vector search", collection_name)
            return []

        query_embedding = get_embeddings([query])[0]

        search_results = client.search(
            collection_name=collection_name,
            data=[query_embedding],
            anns_field="embedding",
            limit=MAX_VECTOR_RESULTS,
            output_fields=["section_id", "text"],
        )

        results: list[dict] = []
        for hits in search_results:
            for hit in hits:
                entity = hit.get("entity", {})
                snippet = entity.get("text", "")[:CONTEXT_CHARS * 2]
                results.append({
                    "section_id": entity.get("section_id", "unknown"),
                    "snippet": snippet,
                    "source": "vector",
                })
        return results

    except ImportError:
        logger.warning("pymilvus not available, skipping vector search")
        return []
    except Exception:
        logger.exception("Milvus vector search failed")
        return []


def _merge_results(
    text_results: list[dict], vector_results: list[dict]
) -> list[dict]:
    """Merge and deduplicate results from text and vector search.

    Prioritizes vector results (more semantically relevant), then appends
    text results for sections not already covered.
    """
    seen_sections: set[str] = set()
    merged: list[dict] = []

    for item in vector_results:
        key = item["section_id"]
        if key not in seen_sections:
            seen_sections.add(key)
            merged.append(item)

    for item in text_results:
        key = item["section_id"]
        if key not in seen_sections:
            seen_sections.add(key)
            merged.append(item)

    return merged
