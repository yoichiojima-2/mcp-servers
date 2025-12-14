#!/bin/bash
# Download sample datasets for testing MCP servers
# Usage: ./scripts/download-sample-data.sh

set -e

WORKSPACE="${HOME}/.mcp-servers/workspace"
DATASETS_DIR="${WORKSPACE}/datasets"

mkdir -p "${DATASETS_DIR}"

echo "Downloading titanic.csv..."
curl -fsSL "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv" \
    -o "${DATASETS_DIR}/titanic.csv" || {
    echo "Error: Failed to download titanic.csv" >&2
    exit 1
}

echo "Sample data downloaded to ${DATASETS_DIR}"
echo "  - titanic.csv (891 passengers)"
