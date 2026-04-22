"""Tests for database operations."""

import tempfile
from pathlib import Path

from mcp_prometheus_documentation.database import DocumentDatabase
from mcp_prometheus_documentation.models import Document


def _make_doc(
    path: str,
    title: str = "Doc",
    content: str = "Content",
    section: str = "docs",
    source: str = "prometheus",
    url: str = "https://prometheus.io/docs/",
    description: str | None = None,
) -> Document:
    return Document(
        path=path,
        title=title,
        description=description,
        section=section,
        content=content,
        url=url,
        source=source,
    )


def test_database_initialisation() -> None:
    """Test database initialisation creates schema."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)
        assert db.db_path == db_path
        assert db_path.exists()


def test_upsert_document() -> None:
    """Test inserting and updating a document."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        doc = _make_doc(
            path="prometheus/docs/concepts/metric_types.md",
            title="Metric Types",
            description="Metric types in Prometheus",
            content="Content about Prometheus metric types",
            url="https://prometheus.io/docs/concepts/metric_types/",
        )

        db.upsert_document(doc)
        retrieved = db.get_document("prometheus/docs/concepts/metric_types.md")

        assert retrieved is not None
        assert retrieved.title == "Metric Types"
        assert retrieved.content == "Content about Prometheus metric types"
        assert retrieved.source == "prometheus"


def test_upsert_document_update() -> None:
    """Test updating an existing document."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        doc1 = _make_doc(
            path="prometheus/docs/concepts/metric_types.md",
            title="Original",
            content="Original content",
        )
        db.upsert_document(doc1)

        doc2 = _make_doc(
            path="prometheus/docs/concepts/metric_types.md",
            title="Updated",
            content="Updated content",
        )
        db.upsert_document(doc2)

        retrieved = db.get_document("prometheus/docs/concepts/metric_types.md")
        assert retrieved is not None
        assert retrieved.title == "Updated"
        assert retrieved.content == "Updated content"


def test_search_documents() -> None:
    """Test searching documents."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        doc1 = _make_doc(
            path="prometheus/doc1.md",
            title="Prometheus Scraping",
            description="Scrape config guide",
            content="This document covers Prometheus scrape configuration",
        )
        doc2 = _make_doc(
            path="prometheus/doc2.md",
            title="Prometheus Alerting",
            description="Alerting guide",
            content="This document covers Prometheus alerting rules",
        )

        db.upsert_document(doc1)
        db.upsert_document(doc2)

        results = db.search("scrape")
        assert len(results) > 0
        assert any("Scraping" in r.title for r in results)


def test_search_with_section_filter() -> None:
    """Test searching with section filter."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        doc1 = _make_doc(
            path="prometheus/docs/doc1.md",
            title="Prometheus Concepts",
            section="docs",
            content="Concept documentation",
        )
        doc2 = _make_doc(
            path="prometheus/blog/doc2.md",
            title="Prometheus Blog Post",
            section="blog",
            content="Blog post about Prometheus",
            url="https://prometheus.io/blog/2020/01/01/post/",
        )

        db.upsert_document(doc1)
        db.upsert_document(doc2)

        results = db.search("Prometheus", section="docs")
        assert len(results) == 1
        assert results[0].section == "docs"


def test_search_with_source_filter() -> None:
    """Test searching with source filter."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        doc1 = _make_doc(
            path="prometheus/docs/overview.md",
            title="Prometheus Overview",
            content="Prometheus is a monitoring system",
            source="prometheus",
        )
        doc2 = _make_doc(
            path="prometheus-operator/getting-started/installation.md",
            title="Installing Prometheus Operator",
            content="Install Prometheus Operator on Kubernetes",
            source="prometheus-operator",
            url="https://prometheus-operator.dev/docs/getting-started/installation/",
        )

        db.upsert_document(doc1)
        db.upsert_document(doc2)

        results = db.search("Prometheus", source="prometheus-operator")
        assert len(results) == 1
        assert results[0].source == "prometheus-operator"


def test_get_document_not_found() -> None:
    """Test getting a non-existent document."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        result = db.get_document("nonexistent.md")
        assert result is None


def test_clear_database() -> None:
    """Test clearing all documents."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        doc = _make_doc(path="prometheus/test.md")
        db.upsert_document(doc)

        assert db.get_document_count() == 1

        db.clear()

        assert db.get_document_count() == 0


def test_get_document_count() -> None:
    """Test getting document count."""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        db = DocumentDatabase(db_path)

        assert db.get_document_count() == 0

        for i in range(5):
            doc = _make_doc(
                path=f"prometheus/doc{i}.md",
                title=f"Doc {i}",
                content=f"Content {i}",
            )
            db.upsert_document(doc)

        assert db.get_document_count() == 5
