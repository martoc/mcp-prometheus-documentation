[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-green.svg)](https://modelcontextprotocol.io/)

# MCP Prometheus Documentation Server

An MCP (Model Context Protocol) server that provides search and retrieval tools for [Prometheus](https://prometheus.io) and [Prometheus Operator](https://prometheus-operator.dev) documentation. This server enables AI assistants like Claude to search and read documentation directly from the upstream repositories.

## Sources

This server indexes documentation from two upstream repositories:

- [`prometheus/docs`](https://github.com/prometheus/docs) — main Prometheus documentation (docs and blog).
- [`prometheus-operator/prometheus-operator`](https://github.com/prometheus-operator/prometheus-operator) — Prometheus Operator documentation (the `Documentation/` directory).

## Features

- **Full-text search** using SQLite FTS5 with BM25 ranking and Porter stemming
- **Section filtering** to narrow search results by documentation category
- **Source filtering** to restrict results to either Prometheus or Prometheus Operator
- **Sparse checkout** for efficient cloning of only the required directories
- **Docker support** for portable deployment across projects
- **STDIO transport** for seamless MCP client integration

## Quick Start

### Using the Container Image (Recommended)

The `martoc/mcp-prometheus-documentation` container image is published to Docker Hub with the documentation index pre-built. Available for `linux/amd64` and `linux/arm64`.

```bash
# Pull and run the server
docker run -i --rm martoc/mcp-prometheus-documentation:latest
```

### Building Locally with Docker

```bash
# Build the Docker image (includes pre-indexed documentation)
make docker-build

# Test the server
make docker-run
```

### Using uv (Local Development)

```bash
# Initialise the environment
make init

# Build the documentation index
make index

# Run the server
make run
```

## Container Image

The `martoc/mcp-prometheus-documentation` container image is published to [Docker Hub](https://hub.docker.com/r/martoc/mcp-prometheus-documentation). It includes the pre-built documentation index so the server is ready to use immediately.

| Property | Value |
|----------|-------|
| Registry | Docker Hub |
| Image | `martoc/mcp-prometheus-documentation` |
| Platforms | `linux/amd64`, `linux/arm64` |
| Base image | `python:3.12-slim` |
| Index | Pre-built at image build time from the `main` branch of each upstream repository |

```bash
# Pull the latest image
docker pull martoc/mcp-prometheus-documentation:latest

# Run the MCP server
docker run -i --rm martoc/mcp-prometheus-documentation:latest
```

## Configuration

### Claude Code / Claude Desktop

Add to your `.mcp.json` or global settings to use the published container image:

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

For a locally built Docker image:

```json
{
  "mcpServers": {
    "prometheus-documentation": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "mcp-prometheus-documentation"]
    }
  }
}
```

For local development without Docker:

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

## MCP Tools

| Tool | Description |
|------|-------------|
| `search_documentation` | Search Prometheus documentation by keyword query with optional section and source filters |
| `read_documentation` | Retrieve the full content of a specific documentation page |

### search_documentation

Search Prometheus and Prometheus Operator documentation using full-text search with stemming support.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | Search terms (supports stemming) |
| `section` | string | No | None | Filter by section (e.g., `docs`, `blog`, `getting-started`) |
| `source` | string | No | None | Filter by source: `prometheus` or `prometheus-operator` |
| `limit` | integer | No | 10 | Maximum results (1-50) |

**Common Prometheus sections:** `docs`, `blog`.

**Common Prometheus Operator sections:** `getting-started`, `user-guides`, `api-reference`, `platform`, `developer`, `proposals`.

### read_documentation

Retrieve the full content of a documentation page.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | Yes | Source-prefixed path to the document (e.g., `prometheus/docs/introduction/overview.md`). This path is returned by `search_documentation`. |

## CLI Commands

```bash
# Build/rebuild the documentation index
uv run prometheus-docs-index index
uv run prometheus-docs-index index --rebuild
uv run prometheus-docs-index index --branch main

# Show index statistics
uv run prometheus-docs-index stats
```

## Development

```bash
make init       # Initialise development environment
make build      # Run full build (lint, typecheck, test)
make test       # Run tests with coverage
make format     # Format code
make lint       # Run linter
make typecheck  # Run type checker
```

## Documentation

- [USAGE.md](USAGE.md) - Detailed usage instructions
- [CODESTYLE.md](CODESTYLE.md) - Code style guidelines
- [CLAUDE.md](CLAUDE.md) - Claude Code instructions

## Licence

This project is licensed under the MIT Licence - see the [LICENSE](LICENSE) file for details.
