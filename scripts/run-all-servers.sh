#!/bin/bash
# Run all MCP servers with SSE transport using uv
# Usage: ./scripts/run-all-servers.sh [start|stop|status]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
PID_DIR="$ROOT_DIR/.pids"

# Server definitions: name:module:port
SERVERS=(
    "browser:browser:8001"
    "data-analysis:data_analysis:8002"
    "docx:docx:8004"
    "frontend-design:frontend_design:8006"
    "nano-banana:nano_banana:8007"
    "o3:o3_search:8008"
    "pdf:pdf:8009"
    "pptx:pptx_mcp:8010"
    "preview:preview:8011"
    "shell:shell:8012"
    "slack:slack:8013"
    "vectorstore:vectorstore:8014"
    "xlsx:xlsx:8015"
)

start_servers() {
    mkdir -p "$PID_DIR"

    echo "Starting MCP servers..."
    for server in "${SERVERS[@]}"; do
        IFS=':' read -r name module port <<< "$server"

        pid_file="$PID_DIR/$name.pid"
        log_file="$PID_DIR/$name.log"

        if [ -f "$pid_file" ] && kill -0 "$(cat "$pid_file")" 2>/dev/null; then
            echo "  $name (port $port) - already running"
            continue
        fi

        cd "$ROOT_DIR/src/$name"
        TRANSPORT=sse PORT="$port" uv run python -m "$module" > "$log_file" 2>&1 &
        echo $! > "$pid_file"
        echo "  $name (port $port) - started (PID: $!)"
    done

    echo ""
    echo "All servers started. Logs in: $PID_DIR/*.log"
}

stop_servers() {
    echo "Stopping MCP servers..."
    for server in "${SERVERS[@]}"; do
        IFS=':' read -r name module port <<< "$server"

        pid_file="$PID_DIR/$name.pid"

        if [ -f "$pid_file" ]; then
            pid=$(cat "$pid_file")
            if kill -0 "$pid" 2>/dev/null; then
                kill "$pid" 2>/dev/null || true
                echo "  $name - stopped (PID: $pid)"
            else
                echo "  $name - not running"
            fi
            rm -f "$pid_file"
        else
            echo "  $name - not running"
        fi
    done
}

status_servers() {
    echo "MCP Server Status:"
    echo ""
    printf "%-20s %-8s %-10s %s\n" "SERVER" "PORT" "STATUS" "PID"
    printf "%-20s %-8s %-10s %s\n" "------" "----" "------" "---"

    for server in "${SERVERS[@]}"; do
        IFS=':' read -r name module port <<< "$server"

        pid_file="$PID_DIR/$name.pid"

        if [ -f "$pid_file" ] && kill -0 "$(cat "$pid_file")" 2>/dev/null; then
            pid=$(cat "$pid_file")
            printf "%-20s %-8s %-10s %s\n" "$name" "$port" "running" "$pid"
        else
            printf "%-20s %-8s %-10s %s\n" "$name" "$port" "stopped" "-"
        fi
    done
}

case "${1:-start}" in
    start)
        start_servers
        ;;
    stop)
        stop_servers
        ;;
    status)
        status_servers
        ;;
    restart)
        stop_servers
        sleep 1
        start_servers
        ;;
    *)
        echo "Usage: $0 {start|stop|status|restart}"
        exit 1
        ;;
esac
