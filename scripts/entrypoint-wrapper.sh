#!/bin/bash
# Wrapper entrypoint (runs as root): NAS symlink -> drop to agent -> OpenAB

# --- NAS symlink ---
if [ -n "$AGENT_NAME" ] && [ -d "/nas/shared" ]; then
    ln -sfn /nas/shared /shared
    echo "[nas-link] /shared -> /nas/shared"

    if [ -d "/nas/agents/$AGENT_NAME/projects" ]; then
        rm -rf /home/agent/projects 2>/dev/null
        ln -sfn "/nas/agents/$AGENT_NAME/projects" /home/agent/projects
        echo "[nas-link] /home/agent/projects -> /nas/agents/$AGENT_NAME/projects"
    fi
fi

# --- Shared steering symlink (as agent) ---
su -s /bin/bash agent -c "/usr/local/bin/link-shared-steering.sh"

# --- Drop privileges and start OpenAB ---
exec setpriv --reuid=agent --regid=agent --init-groups openab "$@"
