"""Parser for Prometheus documentation markdown files."""

import re
from pathlib import Path

import frontmatter  # type: ignore[import-untyped]

from mcp_prometheus_documentation.models import Document, DocumentMetadata


class DocumentParser:
    """Parses markdown files with YAML frontmatter."""

    PROMETHEUS_DOCS_BASE_URL = "https://prometheus.io"
    PROMETHEUS_OPERATOR_DOCS_BASE_URL = "https://prometheus-operator.dev"

    SOURCE_PROMETHEUS = "prometheus"
    SOURCE_PROMETHEUS_OPERATOR = "prometheus-operator"

    BLOG_FILENAME_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-(.+)$")

    def parse_file(self, file_path: Path, base_path: Path, source: str) -> Document | None:
        """Parse a markdown file and extract metadata and content.

        Args:
            file_path: Path to the markdown file.
            base_path: Base path of the documentation directory.
            source: Source identifier for the upstream repository.

        Returns:
            Document instance or None if parsing fails.
        """
        try:
            post = frontmatter.load(file_path)
            metadata = self._extract_metadata(post.metadata, file_path)
            relative_path = file_path.relative_to(base_path)
            section = self._extract_section(relative_path)
            url = self._compute_url(relative_path, source)
            content = self._clean_content(post.content)

            prefixed_path = f"{source}/{relative_path}"

            return Document(
                path=prefixed_path,
                title=metadata.title,
                description=metadata.description,
                section=section,
                content=content,
                url=url,
                source=source,
            )
        except Exception:
            return None

    def _extract_metadata(self, metadata: dict[str, object], file_path: Path) -> DocumentMetadata:
        """Extract structured metadata from frontmatter.

        Args:
            metadata: Dictionary of frontmatter fields.
            file_path: Path to the file for fallback title extraction.

        Returns:
            DocumentMetadata instance.
        """
        title = metadata.get("title")
        if not isinstance(title, str):
            title = file_path.stem.replace("-", " ").replace("_", " ").title()

        description = metadata.get("description")
        if not isinstance(description, str):
            description = None

        return DocumentMetadata(
            title=title,
            description=description,
        )

    def _extract_section(self, relative_path: Path) -> str:
        """Extract the top-level section from the path.

        Args:
            relative_path: Path relative to docs directory.

        Returns:
            Section name (first directory component or 'root').
        """
        parts = relative_path.parts
        return parts[0] if len(parts) > 1 else "root"

    def _compute_url(self, relative_path: Path, source: str) -> str:
        """Compute the documentation URL for the given source.

        Args:
            relative_path: Path relative to the documentation base directory.
            source: Source identifier (prometheus or prometheus-operator).

        Returns:
            Full URL to the documentation page.
        """
        if source == self.SOURCE_PROMETHEUS:
            return self._compute_prometheus_url(relative_path)
        if source == self.SOURCE_PROMETHEUS_OPERATOR:
            return self._compute_prometheus_operator_url(relative_path)
        return ""

    def _compute_prometheus_url(self, relative_path: Path) -> str:
        """Compute the prometheus.io URL for a docs or blog page.

        Args:
            relative_path: Path relative to the prometheus/docs repository root.

        Returns:
            Full URL on prometheus.io.
        """
        parts = relative_path.parts
        base = self.PROMETHEUS_DOCS_BASE_URL

        # Blog posts: blog/posts/YYYY-MM-DD-slug.md -> /blog/YYYY/MM/DD/slug/
        if len(parts) >= 3 and parts[0] == "blog" and parts[1] == "posts":
            stem = Path(parts[-1]).stem
            match = self.BLOG_FILENAME_RE.match(stem)
            if match:
                year, month, day, slug = match.groups()
                return f"{base}/blog/{year}/{month}/{day}/{slug}/"
            return f"{base}/blog/"

        # Docs pages: docs/<category>/<file>.md -> /docs/<category>/<file>/
        path_str = str(relative_path)
        path_str = re.sub(r"\.md$", "", path_str)
        # Hugo-style index pages
        path_str = re.sub(r"/index$", "", path_str)
        if path_str == "index":
            return f"{base}/"
        return f"{base}/{path_str}/"

    def _compute_prometheus_operator_url(self, relative_path: Path) -> str:
        """Compute the prometheus-operator.dev URL for a Documentation page.

        Args:
            relative_path: Path relative to the prometheus-operator/Documentation directory.

        Returns:
            Full URL on prometheus-operator.dev.
        """
        path_str = str(relative_path)
        path_str = re.sub(r"\.md$", "", path_str)
        path_str = re.sub(r"/_index$", "", path_str)
        if path_str == "_index" or not path_str:
            return f"{self.PROMETHEUS_OPERATOR_DOCS_BASE_URL}/docs/"
        return f"{self.PROMETHEUS_OPERATOR_DOCS_BASE_URL}/docs/{path_str}/"

    def _clean_content(self, content: str) -> str:
        """Clean markdown content for indexing.

        Removes Hugo-specific syntax and other markup artefacts.

        Args:
            content: Raw markdown content.

        Returns:
            Cleaned content suitable for indexing.
        """
        # Remove Hugo shortcode tags ({{< >}} form) while preserving inner content
        content = re.sub(r"\{\{<[^>]*>\}\}", "", content)
        # Remove Hugo shortcode tags ({{% %}} form) while preserving inner content
        content = re.sub(r"\{\{%[^%]*%\}\}", "", content)
        # Remove HTML comments
        content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)
        # Remove HTML tags
        content = re.sub(r"<[^>]+>", "", content)
        return content.strip()
