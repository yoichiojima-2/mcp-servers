#!/bin/bash

WORKSPACE="${HOME}/.mcp-servers/data-analysis"

mkdir -p "$WORKSPACE/datasets"
if curl -fL -o "$WORKSPACE/datasets/titanic.csv" https://calmcode.io/static/data/titanic.csv; then
    echo "downloaded titanic dataset to $WORKSPACE/datasets/titanic.csv"
else
    echo "failed to download titanic dataset." >&2
    exit 1
fi
