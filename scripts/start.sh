#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

MODE="normal"
CLEAN=false

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --local    Run from local repository instead of published package"
    echo "  --clean   Clear uv cache before starting"
    echo "  -h, --help Show this help message"
    echo ""
    echo "Modes:"
    echo "  normal (default)  Use published package via 'uvx ableton-mcp'"
    echo "  local            Use local repository code"
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --local)
            MODE="local"
            shift
            ;;
        --clean)
            CLEAN=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Error: Unknown option $1"
            usage
            exit 1
            ;;
    esac
done

if [ "$CLEAN" = true ]; then
    echo "Clearing uv cache..."
    uv cache clean
    echo "Cache cleared."
    echo ""
fi

PROJECT_ROOT="$(pwd)"

if [ "$MODE" = "local" ]; then
    EXEC_CMD="uv run --project \"$REPO_ROOT\" ableton-mcp"
    echo "========================================="
    echo "Running in LOCAL development mode"
    echo "========================================="
    echo "Mode:         local (development)"
    echo "Executor:     uv run --project <repo>"
    echo "Project root: $REPO_ROOT"
    echo "Command:      $EXEC_CMD"
    echo "========================================="
    echo ""
    echo "Starting MCP Server from local checkout..."
    uv run --project "$REPO_ROOT" ableton-mcp
else
    EXEC_CMD="uvx ableton-mcp"
    echo "========================================="
    echo "Running in NORMAL user mode"
    echo "========================================="
    echo "Mode:         normal (published package)"
    echo "Executor:     uvx ableton-mcp"
    echo "========================================="
    echo ""
    echo "Starting MCP Server from published package..."
    uvx ableton-mcp
fi