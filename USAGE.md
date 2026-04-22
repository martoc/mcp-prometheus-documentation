# Usage Guide

This guide provides detailed instructions for using the MCP Prometheus Documentation Server.

## Installation

### Prerequisites

- Python 3.12 or later
- [uv](https://docs.astral.sh/uv/) package manager
- Git
- Docker (optional, for containerised deployment)

### Local Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/martoc/mcp-prometheus-documentation.git
   cd mcp-prometheus-documentation
   ```

2. Initialise the development environment:
   ```bash
   make init
   ```

3. Build the documentation index:
   ```bash
   make index
   ```

## Indexing Documentation

### Initial Indexing

Index Prometheus and Prometheus Operator documentation from the main branches of their upstream repositories:

```bash
uv run prometheus-docs-index index
```

### Rebuilding the Index

Clear the existing index and rebuild from scratch:

```bash
uv run prometheus-docs-index index --rebuild
```

### Indexing a Specific Branch

Index documentation from a specific Git branch (applied to every upstream source):

```bash
uv run prometheus-docs-index index --branch release-2.50
```

### Index Statistics

View the number of indexed documents:

```bash
uv run prometheus-docs-index stats
```

## Running the MCP Server

### Using the Container Image (Recommended)

The `martoc/mcp-prometheus-documentation` container image is published to Docker Hub with the documentation index pre-built. Available for `linux/amd64` and `linux/arm64`.

```bash
# Pull and run the server
docker run -i --rm martoc/mcp-prometheus-documentation:latest
```

### Local Development

Run the server directly using uv:

```bash
make run
# or
uv run mcp-prometheus-documentation
```

### Building a Local Docker Image

Build and run the server in a Docker container:

```bash
make docker-build
make docker-run
```

## MCP Client Configuration

### Claude Code (Container Image)

Add to your project's `.mcp.json` to use the published container image:

```json
{
  "mcpServers": {
    "prometheus-documentation": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "martoc/mcp-prometheus-documentation:latest"]
    }
  }
}
```

### Claude Code (Local Development)

Add to your project's `.mcp.json` for local development:

```json
{
  "mcpServers": {
    "prometheus-documentation": {
      "command": "uv",
      "args": ["run", "mcp-prometheus-documentation"],
      "cwd": "/path/to/mcp-prometheus-documentation"
    }
  }
}
```

### Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "prometheus-documentation": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "martoc/mcp-prometheus-documentation:latest"]
    }
  }
}
```

## Using the Tools

### Searching Documentation

Search for topics across Prometheus documentation:

```
Search for "scrape configuration"
Search for "alerting rules" in section "docs"
Search for "service monitor" in source "prometheus-operator"
Search for "histogram" with limit 20
```

Example response:

```json
{
  "query": "scrape configuration",
  "section_filter": null,
  "source_filter": null,
  "result_count": 3,
  "results": [
    {
      "title": "Configuration",
      "url": "https://prometheus.io/docs/prometheus/latest/configuration/configuration/",
      "path": "prometheus/docs/prometheus/latest/configuration/configuration.md",
      "section": "docs",
      "source": "prometheus",
      "snippet": "...scrape_configs specify a set of targets...",
      "relevance_score": 12.5432
    }
  ]
}
```

### Reading Documentation

Retrieve the full content of a specific page:

```
Read documentation at path "prometheus/docs/introduction/overview.md"
Read documentation at path "prometheus-operator/getting-started/installation.md"
```

Example response:

```json
{
  "path": "prometheus/docs/introduction/overview.md",
  "title": "Overview",
  "description": null,
  "section": "docs",
  "source": "prometheus",
  "url": "https://prometheus.io/docs/introduction/overview/",
  "content": "## What is Prometheus?\n\n..."
}
```

## Sources and Sections

The server indexes two upstream sources:

- **prometheus** — files from [`prometheus/docs`](https://github.com/prometheus/docs), serving the `https://prometheus.io` site.
  Common sections: `docs`, `blog`.
- **prometheus-operator** — files from the `Documentation/` directory of [`prometheus-operator/prometheus-operator`](https://github.com/prometheus-operator/prometheus-operator), serving the `https://prometheus-operator.dev` site.
  Common sections: `getting-started`, `user-guides`, `api-reference`, `platform`, `developer`, `proposals`.

Use the `source` and `section` parameters to narrow search results.

## Development Workflow

### Code Quality Checks

Run all code quality checks:

```bash
make build
```

This runs:
- Linter (ruff)
- Type checker (mypy)
- Tests with coverage (pytest)

### Individual Checks

```bash
make lint       # Run linter only
make typecheck  # Run type checker only
make test       # Run tests only
make format     # Format code
```

### Updating Dependencies

Update the lock file:

```bash
make generate
```

## Troubleshooting

### Index Build Fails

If the index build fails, try:

1. Check your internet connection
2. Verify Git is installed and accessible
3. Try rebuilding with a different branch:
   ```bash
   uv run prometheus-docs-index index --rebuild --branch main
   ```

### No Search Results

If searches return no results:

1. Verify the index is built:
   ```bash
   uv run prometheus-docs-index stats
   ```

2. Rebuild the index if necessary:
   ```bash
   uv run prometheus-docs-index index --rebuild
   ```

### Database Location

The default database location is `data/prometheus_docs.db`. To use a custom location:

```bash
uv run prometheus-docs-index index --database /path/to/custom.db
```

## Performance Considerations

- **Initial indexing**: May take several minutes depending on network speed
- **Sparse checkout**: Only the `docs/` and `blog/` directories of `prometheus/docs`, and the `Documentation/` directory of `prometheus-operator/prometheus-operator`, are fetched
- **Search performance**: FTS5 with BM25 ranking provides fast, relevant results
- **Memory usage**: Minimal during operation; database is SQLite-based
