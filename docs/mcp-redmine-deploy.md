# Redmine MCP Server 部署指南

## 概述

- 套件：[redmine-mcp-server](https://pypi.org/project/redmine-mcp-server/)（PyPI）
- 來源：[jztan/redmine-mcp-server](https://github.com/jztan/redmine-mcp-server)
- 傳輸方式：HTTP Streamable（endpoint: `/mcp`）
- 健康檢查：`GET /health`

## 特點

- HTTP Streamable transport — 標準 HTTP POST，跨主機連線無障礙
- 21 個專用工具 — issue CRUD、wiki、time tracking、搜尋、專案摘要
- Docker Ready
- 多種認證方式 — API Key、帳號密碼、OAuth2（OAuth2 需 Redmine 6.1+）
- 唯讀模式 — 可透過環境變數限制為唯讀，適合初期測試
- 健康檢查 — 內建 `/health` endpoint

## 部署（Docker）

### Dockerfile

```dockerfile
FROM python:3.13-slim
RUN pip install --no-cache-dir redmine-mcp-server
EXPOSE 8000
CMD ["redmine-mcp-server"]
```

### docker-compose.yml

```yaml
services:
  mcp-redmine:
    build: .
    container_name: mcp-redmine
    restart: unless-stopped
    ports:
      - "9500:8000"
    environment:
      - REDMINE_URL=${REDMINE_URL}
      - REDMINE_API_KEY=${REDMINE_API_KEY}
      - SERVER_HOST=0.0.0.0
      - SERVER_PORT=8000
```

### .env

```env
REDMINE_URL=http://your-redmine-host:port
REDMINE_API_KEY=your-api-key
```

### 啟動與驗證

```bash
docker compose up -d --build

# 健康檢查
curl http://localhost:9500/health
# 預期：{"status":"ok","service":"redmine_mcp_tools","auth_mode":"legacy"}
```

## 環境變數

| 變數 | 必要 | 預設值 | 說明 |
|------|------|--------|------|
| `REDMINE_URL` | ✅ | — | Redmine 網址 |
| `REDMINE_API_KEY` | ✅† | — | Redmine API Key（legacy 模式） |
| `REDMINE_AUTH_MODE` | ❌ | `legacy` | 認證模式：`legacy` 或 `oauth` |
| `SERVER_HOST` | ❌ | `0.0.0.0` | 綁定的 host |
| `SERVER_PORT` | ❌ | `8000` | 綁定的 port |
| `REDMINE_SSL_VERIFY` | ❌ | `true` | SSL 驗證 |
| `REDMINE_MCP_READ_ONLY` | ❌ | `false` | 唯讀模式 |
| `ATTACHMENTS_DIR` | ❌ | `./attachments` | 附件下載目錄 |
| `AUTO_CLEANUP_ENABLED` | ❌ | `true` | 自動清理過期附件 |

† legacy 模式下必填。也可改用 `REDMINE_USERNAME` + `REDMINE_PASSWORD`。

## 認證模式

### Legacy（預設）

一個 instance 綁定一組 API Key，所有 request 使用同一身份。

### OAuth2（需 Redmine 6.1+）

每個 MCP request 帶各自的 `Authorization: Bearer <token>`，server 會向 Redmine 驗證 token。
適用於多使用者場景，每人用自己的 Redmine 帳號操作。

設定方式：
```env
REDMINE_AUTH_MODE=oauth
REDMINE_URL=https://redmine.example.com
REDMINE_MCP_BASE_URL=https://redmine-mcp.example.com
```

需在 Redmine 管理後台註冊 OAuth application。詳見套件文件。

## 多帳號部署（Legacy 模式）

Legacy 模式下若需多個身份各自操作，需部署多個 instance，各自帶不同的 API Key，用不同 port：

```yaml
services:
  mcp-redmine-user-a:
    build: .
    ports: ["9501:8000"]
    environment:
      - REDMINE_URL=${REDMINE_URL}
      - REDMINE_API_KEY=${API_KEY_USER_A}
      - SERVER_HOST=0.0.0.0
      - SERVER_PORT=8000

  mcp-redmine-user-b:
    build: .
    ports: ["9502:8000"]
    environment:
      - REDMINE_URL=${REDMINE_URL}
      - REDMINE_API_KEY=${API_KEY_USER_B}
      - SERVER_HOST=0.0.0.0
      - SERVER_PORT=8000
```
