#!/bin/bash
# Link shared steering files to agent's .kiro/steering directory

# Try /opt/steering first (local bind mount), fallback to /shared/steering (NAS)
if [ -d "/opt/steering" ]; then
    SHARED_DIR="/opt/steering"
elif [ -d "/shared/steering" ]; then
    SHARED_DIR="/shared/steering"
else
    echo "[link-shared-steering] no steering source found, skipping"
    exit 0
fi

STEERING_DIR="/home/agent/.kiro/steering"
mkdir -p "$STEERING_DIR"

for file in "$SHARED_DIR"/*.md; do
    [ -f "$file" ] || continue
    filename=$(basename "$file")
    target="$STEERING_DIR/$filename"
    if [ -f "$target" ] && [ ! -L "$target" ]; then
        mv "$target" "$target.bak"
    fi
    ln -sf "$file" "$target"
done

echo "[link-shared-steering] done: $(ls "$SHARED_DIR"/*.md 2>/dev/null | wc -l) files linked from $SHARED_DIR"
