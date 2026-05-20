FROM ghcr.io/openabdev/openab:0.8.3-beta.5
USER root
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*
# GitHub CLI — Agent 開 PR、管理 PR 用
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
      -o /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
      > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update && apt-get install -y --no-install-recommends gh \
    && rm -rf /var/lib/apt/lists/*

# 共用 steering 文件 symlink 腳本（容器啟動時由 entrypoint wrapper 執行）
COPY scripts/link-shared-steering.sh /usr/local/bin/link-shared-steering.sh
COPY scripts/entrypoint-wrapper.sh /usr/local/bin/entrypoint-wrapper.sh
RUN chmod +x /usr/local/bin/link-shared-steering.sh /usr/local/bin/entrypoint-wrapper.sh

# 預建 /nas 目錄
RUN mkdir -p /nas

# 以 root 啟動，entrypoint 建完 symlink 後降權為 agent
ENTRYPOINT ["/usr/local/bin/entrypoint-wrapper.sh"]
