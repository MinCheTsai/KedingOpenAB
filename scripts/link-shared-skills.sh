#!/bin/bash
# Link shared skills to agent's .kiro/skills directory
# Only links skills listed in AGENT_SKILLS env var (comma-separated)
# Example: AGENT_SKILLS=xlsx,pr-review

# Try /opt/skills first (local bind mount), fallback to /shared/skills (NAS)
if [ -d "/opt/skills" ]; then
    SHARED_DIR="/opt/skills"
elif [ -d "/shared/skills" ]; then
    SHARED_DIR="/shared/skills"
else
    echo "[link-shared-skills] no skills source found, skipping"
    exit 0
fi

# If AGENT_SKILLS is not set or empty, skip
if [ -z "$AGENT_SKILLS" ]; then
    echo "[link-shared-skills] AGENT_SKILLS not set, skipping"
    exit 0
fi

SKILLS_DIR="/home/agent/.kiro/skills"
mkdir -p "$SKILLS_DIR"

linked=0
IFS=',' read -ra SKILLS <<< "$AGENT_SKILLS"
for skill in "${SKILLS[@]}"; do
    # Trim whitespace
    skill=$(echo "$skill" | xargs)
    [ -z "$skill" ] && continue

    if [ -d "$SHARED_DIR/$skill" ] && [ -f "$SHARED_DIR/$skill/SKILL.md" ]; then
        # Remove existing (file or symlink) to avoid conflicts
        rm -rf "$SKILLS_DIR/$skill" 2>/dev/null
        ln -sfn "$SHARED_DIR/$skill" "$SKILLS_DIR/$skill"
        linked=$((linked + 1))
    else
        echo "[link-shared-skills] WARNING: skill '$skill' not found in $SHARED_DIR"
    fi
done

echo "[link-shared-skills] done: $linked skill(s) linked from $SHARED_DIR"
