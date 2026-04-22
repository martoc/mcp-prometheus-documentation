"""Indexer for Prometheus documentation from upstream GitHub repositories."""

import logging
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from mcp_prometheus_documentation.database import DocumentDatabase
from mcp_prometheus_documentation.parser import DocumentParser

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DocsSource:
    """Configuration for a documentation source repository."""

    name: str
    repo_url: str
    sparse_paths: tuple[str, ...]
    content_subpath: str


class PrometheusDocsIndexer:
    """Indexes Prometheus and Prometheus Operator documentation from GitHub."""

    SOURCES: ClassVar[tuple[DocsSource, ...]] = (
        DocsSource(
            name="prometheus",
            repo_url="https://github.com/prometheus/docs.git",
            sparse_paths=("docs", "blog"),
            content_subpath=".",
        ),
        DocsSource(
            name="prometheus-operator",
            repo_url="https://github.com/prometheus-operator/prometheus-operator.git",
            sparse_paths=("Documentation",),
            content_subpath="Documentation",
        ),
    )

    def __init__(self, database: DocumentDatabase) -> None:
        """Initialise indexer with database instance.

        Args:
            database: DocumentDatabase instance for storing documents.
        """
        self.database = database
        self.parser = DocumentParser()

    def index_from_git(self, branch: str = "main", shallow: bool = True) -> int:
        """Clone upstream repositories and index documentation.

        Args:
            branch: Git branch to clone for each source.
            shallow: Whether to do a shallow clone.

        Returns:
            Total number of documents indexed across all sources.
        """
        total = 0
        for source in self.SOURCES:
            with tempfile.TemporaryDirectory() as temp_dir:
                repo_path = Path(temp_dir) / source.name
                self._clone_repository(source, repo_path, branch, shallow)
                total += self._index_source(source, repo_path)
        logger.info("Successfully indexed %d documents in total", total)
        return total

    def index_from_path(self, source_name: str, docs_path: Path) -> int:
        """Index documentation from a local path for a specific source.

        Args:
            source_name: Name of the documentation source.
            docs_path: Path to the repository root directory.

        Returns:
            Number of documents indexed.

        Raises:
            ValueError: If the source name is not recognised.
        """
        source = self._find_source(source_name)
        return self._index_source(source, docs_path)

    def _find_source(self, name: str) -> DocsSource:
        """Find a source by name.

        Args:
            name: Source name.

        Returns:
            DocsSource instance.

        Raises:
            ValueError: If the source is not found.
        """
        for source in self.SOURCES:
            if source.name == name:
                return source
        msg = f"Unknown documentation source: {name}"
        raise ValueError(msg)

    def _clone_repository(
        self,
        source: DocsSource,
        target_path: Path,
        branch: str,
        shallow: bool,
    ) -> None:
        """Clone a documentation repository.

        Args:
            source: Documentation source configuration.
            target_path: Directory to clone into.
            branch: Git branch to clone.
            shallow: Whether to do a shallow clone.
        """
        cmd = ["git", "clone"]
        if shallow:
            cmd.extend(["--depth", "1", "--filter=blob:none", "--sparse"])
        cmd.extend(["--branch", branch, source.repo_url, str(target_path)])

        logger.info("Cloning %s (%s)...", source.name, source.repo_url)
        subprocess.run(cmd, check=True, capture_output=True)  # noqa: S603

        if shallow:
            logger.info("Setting up sparse checkout for %s...", source.name)
            subprocess.run(  # noqa: S603
                ["git", "-C", str(target_path), "sparse-checkout", "set", *source.sparse_paths],  # noqa: S607
                check=True,
                capture_output=True,
            )

        logger.info("Repository %s cloned successfully", source.name)

    def _index_source(self, source: DocsSource, repo_path: Path) -> int:
        """Index all markdown files for a source.

        Args:
            source: Documentation source configuration.
            repo_path: Path to the cloned repository root.

        Returns:
            Number of documents indexed.

        Raises:
            ValueError: If the content path does not exist.
        """
        content_path = repo_path / source.content_subpath if source.content_subpath != "." else repo_path
        if not content_path.exists():
            msg = f"Content path does not exist: {content_path}"
            raise ValueError(msg)

        md_files = [f for f in content_path.rglob("*.md") if self._should_index(f, source)]
        logger.info("Found %d markdown files for %s", len(md_files), source.name)

        indexed_count = 0
        for file_path in md_files:
            document = self.parser.parse_file(file_path, content_path, source.name)
            if document:
                self.database.upsert_document(document)
                indexed_count += 1
                logger.debug("Indexed: %s", document.path)
            else:
                logger.warning("Failed to parse: %s", file_path)

        logger.info("Indexed %d markdown documents for %s", indexed_count, source.name)
        return indexed_count

    def _should_index(self, file_path: Path, source: DocsSource) -> bool:
        """Determine whether a markdown file should be indexed.

        Args:
            file_path: Absolute path to the markdown file.
            source: Documentation source configuration.

        Returns:
            True if the file should be indexed.
        """
        # Skip top-level repository docs like README.md, CONTRIBUTING.md etc.
        name_lower = file_path.name.lower()
        excluded_filenames = {
            "readme.md",
            "contributing.md",
            "code_of_conduct.md",
            "security.md",
            "maintainers.md",
            "changelog.md",
            "governance.md",
            "markdown-guide.md",
            "notice.md",
        }
        if name_lower in excluded_filenames:
            return False
        return True

    def rebuild_index(self, branch: str = "main") -> int:
        """Clear existing index and rebuild from scratch.

        Args:
            branch: Git branch to index from.

        Returns:
            Number of documents indexed.
        """
        logger.info("Clearing existing index...")
        self.database.clear()
        return self.index_from_git(branch)
