"""Tests for data models."""

from mcp_prometheus_documentation.models import Document, DocumentMetadata, SearchResult


def test_document_metadata_creation() -> None:
    """Test creating a DocumentMetadata instance."""
    metadata = DocumentMetadata(
        title="Prometheus Overview",
        description="Introduction to Prometheus monitoring",
    )
    assert metadata.title == "Prometheus Overview"
    assert metadata.description == "Introduction to Prometheus monitoring"


def test_document_metadata_optional_fields() -> None:
    """Test DocumentMetadata with optional fields."""
    metadata = DocumentMetadata(title="Overview")
    assert metadata.title == "Overview"
    assert metadata.description is None


def test_document_creation() -> None:
    """Test creating a Document instance."""
    doc = Document(
        path="prometheus/docs/introduction/overview.md",
        title="Overview",
        description="Prometheus overview",
        section="docs",
        content="# Overview\n\nContent here",
        url="https://prometheus.io/docs/introduction/overview/",
        source="prometheus",
    )
    assert doc.path == "prometheus/docs/introduction/overview.md"
    assert doc.title == "Overview"
    assert doc.section == "docs"
    assert doc.source == "prometheus"
    assert "Content here" in doc.content


def test_search_result_creation() -> None:
    """Test creating a SearchResult instance."""
    result = SearchResult(
        path="prometheus/docs/introduction/overview.md",
        title="Overview",
        url="https://prometheus.io/docs/introduction/overview/",
        snippet="...Prometheus collects metrics...",
        score=12.5,
        section="docs",
        source="prometheus",
    )
    assert result.path == "prometheus/docs/introduction/overview.md"
    assert result.score == 12.5
    assert result.section == "docs"
    assert result.source == "prometheus"
