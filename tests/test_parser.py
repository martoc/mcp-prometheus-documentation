"""Tests for document parser."""

import tempfile
from pathlib import Path

from mcp_prometheus_documentation.parser import DocumentParser


def test_extract_section_root() -> None:
    """Test extracting section from root-level file."""
    parser = DocumentParser()
    section = parser._extract_section(Path("index.md"))
    assert section == "root"


def test_extract_section_nested() -> None:
    """Test extracting section from nested file."""
    parser = DocumentParser()
    section = parser._extract_section(Path("docs/introduction/overview.md"))
    assert section == "docs"


def test_compute_prometheus_url_docs() -> None:
    """Test computing URL for a Prometheus docs file."""
    parser = DocumentParser()
    url = parser._compute_url(
        Path("docs/introduction/overview.md"),
        DocumentParser.SOURCE_PROMETHEUS,
    )
    assert url == "https://prometheus.io/docs/introduction/overview/"


def test_compute_prometheus_url_blog_post() -> None:
    """Test computing URL for a Prometheus blog post."""
    parser = DocumentParser()
    url = parser._compute_url(
        Path("blog/posts/2015-04-24-prometheus-monitoring-spreads.md"),
        DocumentParser.SOURCE_PROMETHEUS,
    )
    assert url == "https://prometheus.io/blog/2015/04/24/prometheus-monitoring-spreads/"


def test_compute_prometheus_url_index_file() -> None:
    """Test computing URL for a docs index file."""
    parser = DocumentParser()
    url = parser._compute_url(
        Path("docs/introduction/index.md"),
        DocumentParser.SOURCE_PROMETHEUS,
    )
    assert url == "https://prometheus.io/docs/introduction/"


def test_compute_prometheus_operator_url() -> None:
    """Test computing URL for a Prometheus Operator docs file."""
    parser = DocumentParser()
    url = parser._compute_url(
        Path("getting-started/installation.md"),
        DocumentParser.SOURCE_PROMETHEUS_OPERATOR,
    )
    assert url == "https://prometheus-operator.dev/docs/getting-started/installation/"


def test_compute_prometheus_operator_url_top_level() -> None:
    """Test computing URL for a top-level Prometheus Operator docs file."""
    parser = DocumentParser()
    url = parser._compute_url(
        Path("custom-configuration.md"),
        DocumentParser.SOURCE_PROMETHEUS_OPERATOR,
    )
    assert url == "https://prometheus-operator.dev/docs/custom-configuration/"


def test_clean_content_removes_hugo_shortcodes() -> None:
    """Test cleaning content removes Hugo shortcode tags."""
    parser = DocumentParser()
    content = "{{< note >}}\nThis is a note.\n{{< /note >}}\nRegular content."
    cleaned = parser._clean_content(content)
    assert "{{<" not in cleaned
    assert "This is a note." in cleaned
    assert "Regular content." in cleaned


def test_clean_content_removes_html_comments() -> None:
    """Test cleaning content removes HTML comments."""
    parser = DocumentParser()
    content = "<!-- Comment -->\nContent\n<!-- Another -->"
    cleaned = parser._clean_content(content)
    assert "<!--" not in cleaned
    assert "Content" in cleaned


def test_parse_file_with_frontmatter() -> None:
    """Test parsing a file with YAML frontmatter."""
    parser = DocumentParser()

    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)
        file_path = base_path / "docs" / "introduction" / "overview.md"
        file_path.parent.mkdir(parents=True)

        content = """---
title: Overview
sort_rank: 1
---

## What is Prometheus?

Prometheus is an open-source monitoring system.
"""
        file_path.write_text(content)

        doc = parser.parse_file(file_path, base_path, DocumentParser.SOURCE_PROMETHEUS)

        assert doc is not None
        assert doc.title == "Overview"
        assert "Prometheus" in doc.content
        assert doc.path == "prometheus/docs/introduction/overview.md"
        assert doc.section == "docs"
        assert doc.source == "prometheus"
        assert doc.url == "https://prometheus.io/docs/introduction/overview/"


def test_parse_file_prometheus_operator() -> None:
    """Test parsing a Prometheus Operator documentation file."""
    parser = DocumentParser()

    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)
        file_path = base_path / "getting-started" / "installation.md"
        file_path.parent.mkdir(parents=True)

        content = """---
weight: 102
title: Installing Prometheus Operator
description: Installation guide for Prometheus Operator.
---

There are different approaches to install Prometheus Operator.
"""
        file_path.write_text(content)

        doc = parser.parse_file(file_path, base_path, DocumentParser.SOURCE_PROMETHEUS_OPERATOR)

        assert doc is not None
        assert doc.title == "Installing Prometheus Operator"
        assert doc.description == "Installation guide for Prometheus Operator."
        assert doc.section == "getting-started"
        assert doc.source == "prometheus-operator"
        assert doc.url == "https://prometheus-operator.dev/docs/getting-started/installation/"
        assert doc.path == "prometheus-operator/getting-started/installation.md"


def test_parse_file_without_frontmatter() -> None:
    """Test parsing a file without YAML frontmatter."""
    parser = DocumentParser()

    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)
        file_path = base_path / "test-file.md"

        content = "# Test Content\n\nThis is a test."
        file_path.write_text(content)

        doc = parser.parse_file(file_path, base_path, DocumentParser.SOURCE_PROMETHEUS)

        assert doc is not None
        assert doc.title == "Test File"  # Fallback from filename
        assert "Test Content" in doc.content
