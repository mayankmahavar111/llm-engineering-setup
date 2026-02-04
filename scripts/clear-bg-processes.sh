#!/bin/bash

# Script to clear Claude background processes
# This helps improve performance when too many background tasks are running

echo "🧹 Clearing Claude background processes..."
echo ""

# Kill orphaned find processes
find_count=$(pkill -f "find.*claude" 2>/dev/null; echo $?)
if [[ $find_count -eq 0 ]]; then
    echo "✓ Killed find processes related to claude"
fi

# Kill any stuck node processes from Claude (but not the main ones)
# Get the main claude PID
main_claude_pid=$(pgrep -x claude | head -1)

if [[ -n "$main_claude_pid" ]]; then
    # Kill orphaned child processes that are stuck
    for pid in $(pgrep -P "$main_claude_pid" 2>/dev/null); do
        # Check if process has been running for more than 2 minutes (likely stuck)
        runtime=$(ps -o etime= -p "$pid" 2>/dev/null | awk -F: '{if (NF==3) print ($1*3600)+($2*60)+$3; else if (NF==2) print ($1*60)+$2; else print $1}')

        if [[ -n "$runtime" ]] && [[ $runtime -gt 120 ]]; then
            process_name=$(ps -o comm= -p "$pid" 2>/dev/null)
            echo "✓ Killing stuck process: $process_name (PID: $pid, runtime: ${runtime}s)"
            kill -9 "$pid" 2>/dev/null
        fi
    done
fi

# Clear statusline cache to force refresh
cache_file="$HOME/.claude/cache/statusline_cache"
if [[ -f "$cache_file" ]]; then
    rm -f "$cache_file"
    echo "✓ Cleared statusline cache"
fi

# Show current background process count
echo ""
if [[ -n "$main_claude_pid" ]]; then
    bg_count=$(pgrep -P "$main_claude_pid" 2>/dev/null | wc -l | tr -d ' ')
    echo "Current background processes: $bg_count"
else
    echo "Claude main process not found"
fi

# Show system load
echo ""
echo "System status:"
uptime | awk '{print "Load average: " $(NF-2) " " $(NF-1) " " $NF}'

echo ""
echo "✅ Cleanup complete!"
