# MCP Redmine Server 建置與維運指南（已過時）

> ⚠️ **本文件已過時**（2026-04-16）
> 此文件記錄的是 runekaagaard/mcp-redmine（SSE transport）的部署方式。
> 因 DNS rebinding protection 問題，已改用 jztan/redmine-mcp-server（HTTP Streamable）。
> 新方案的部署指南請參考 `docs/mcp-redmine-deploy.md`。
> 本文件保留作為歷史參考，記錄當時的研究過程和踩坑經驗。

---

> 本文件記錄如何透過 Docker 建置並啟動 mcp-redmine MCP server，供 AI agent 連接公司 Redmine。

## 概述

- 專案來源：[runekaagaard/mcp-redmine](https://github.com/runekaagaard/mcp-redmine)
- 用途：讓 AI agent 透過 MCP 協定存取 Redmine API（讀取/更新 issue、新增留言等）
- 通訊模式：stdio（MCP client spawn container 作為子程序）
- 每個 agent 角色使用各自的 Redmine 帳號 + API Key，確保操作紀錄可區分身份

## 前置需求

- Docker（本機或 WSL 環境皆可）
- Git（用於 clone 原始碼）
- 公司 Redmine 的網址與 API Key

## 第一步：Build Docker Image

```bash
# clone 原始碼
git clone https://github.com/runekaagaard/mcp-redmine.git

# 進入目錄並 build image
cd mcp-redmine
docker build -t mcp-redmine .
```

build 完成後可確認 image 存在：

```bash
docker images | grep mcp-redmine
```

## 第二步：測試啟動

手動測試 container 能否正常啟動（stdio 模式會等待輸入，按 Ctrl+C 結束即可）：

```bash
docker run -i --rm \
  -e REDMINE_URL=http://192.168.1.84:800 \
  -e REDMINE_API_KEY=<your_api_key> \
  mcp-redmine
```

如果沒有報錯，代表 image 正常。

## 第三步：設定 MCP Client Config

MCP server 是由 MCP client（如 Kiro）透過 stdio 啟動的，不需要手動 `docker run`。
設定檔放在各角色的 `.kiro/settings/mcp.json`。

範例（海綿寶寶）：

```json
{
  "mcpServers": {
    "redmine": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "REDMINE_URL",
        "-e", "REDMINE_API_KEY",
        "mcp-redmine"
      ],
      "env": {
        "REDMINE_URL": "http://192.168.1.84:800",
        "REDMINE_API_KEY": "<海綿寶寶的 API Key>"
      }
    }
  }
}
```

每個角色各自一份 config，帶各自的 `REDMINE_API_KEY`。

## 環境變數說明

| 變數 | 必要 | 說明 |
|------|------|------|
| `REDMINE_URL` | ✅ | 公司 Redmine 網址，支援子路徑（如 `http://host/redmine/`） |
| `REDMINE_API_KEY` | ✅ | Redmine 帳號的 API Key |
| `REDMINE_HEADERS` | ❌ | 自訂 HTTP headers，格式：`"Header1: Value1, Header2: Value2"` |
| `REDMINE_RESPONSE_FORMAT` | ❌ | 回應格式：`yaml`（預設）或 `json` |
| `REDMINE_ALLOWED_DIRECTORIES` | ❌ | 允許上傳/下載的目錄，逗號分隔。未設定則停用檔案操作 |
| `REDMINE_REQUEST_INSTRUCTIONS` | ❌ | 額外指示檔案路徑（container 內路徑） |

## 可用的 MCP Tools

| Tool | 說明 |
|------|------|
| `redmine_request` | 對 Redmine API 發送請求（GET/POST/PUT/DELETE） |
| `redmine_paths_list` | 列出所有可用的 API 路徑 |
| `redmine_paths_info` | 查詢特定 API 路徑的規格 |
| `redmine_upload` | 上傳檔案到 Redmine |
| `redmine_download` | 從 Redmine 下載附件 |

## 常用 Redmine API 操作範例

透過 `redmine_request` tool：

```
# 列出專案
GET /projects.json

# 列出 issue
GET /issues.json

# 搜尋特定標題的 issue
GET /issues.json?subject=~關鍵字

# 讀取單一 issue
GET /issues/{id}.json

# 新增留言
PUT /issues/{id}.json  data: {"issue": {"notes": "留言內容"}}

# 更新狀態
PUT /issues/{id}.json  data: {"issue": {"status_id": 3}}

# 查詢可用狀態
GET /issue_statuses.json
```

## 安全注意事項

- API Key 等同帳號密碼，不要寫死在程式碼或 commit 到 git
- 在 Redmine 管理後台限制 agent 帳號的角色權限（最小權限原則）
- `REDMINE_ALLOWED_DIRECTORIES` 未設定時，檔案上傳/下載功能會自動停用

## 故障排除

1. **Container 啟動失敗** — 確認 Docker image 已 build（`docker images | grep mcp-redmine`）
2. **連不到 Redmine** — 確認 `REDMINE_URL` 可從 Docker container 內存取（注意 WSL/Docker 網路）
3. **API 回傳 401** — API Key 錯誤或帳號被停用
4. **API 回傳 403** — 帳號權限不足，到 Redmine 管理後台檢查角色設定
5. **Docker 網路問題** — 如果 Redmine 在 host 上，可能需要加 `--network host` 或使用 `host.docker.internal`
