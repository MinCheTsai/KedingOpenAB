# 🐚 神奇海螺 (Magic Conch)

輕量容器管理 Bot，以 Slash Command 操作，不走 OpenAB / kiro-cli。

## 類型

腳本型 Discord Bot（Python + discord.py + docker SDK）

## 職責

- 容器生命管理（重啟 / 停止 / 診斷）
- 狀態查詢（log / rollcall）
- Thread 封存（對話過長時開新 thread 延續）

## 使用頻道

- 容器管理指令：僅限「🏥 急診室」頻道（ID: 1505752303624392755）
- `/conch-archive`：任何 thread 皆可使用

## 程式碼位置

`services/magic-conch/`

## 指令集

| 指令 | 功能 | 權限 | 頻道限制 |
|------|------|------|---------|
| `/conch-status [target]` | 查看狀態 | 所有人 | 急診室 |
| `/conch-heal [target]` | 重啟容器 | 操作員 | 急診室 |
| `/conch-kill [target]` | 停止容器 | 管理員 | 急診室 |
| `/conch-diagnose [target]` | 健康診斷 | 所有人 | 急診室 |
| `/conch-logs [target] [lines]` | 查看 log | 所有人 | 急診室 |
| `/conch-rollcall` | 全員點名 | 所有人 | 急診室 |
| `/conch-restart-all [confirm]` | 全員重啟 | 管理員 | 急診室 |
| `/conch-archive [reason]` | 封存 thread，開新 thread 延續對話 | 操作員 | 任何 thread |

## 環境變數

| 變數 | 說明 |
|------|------|
| `DISCORD_BOT_TOKEN_CONCH` | Bot Token |
| `DISCORD_GUILD_ID` | Guild ID（共用） |
| `CONCH_CHANNEL_ID` | 限定使用頻道（急診室） |
| `CONCH_ADMIN_IDS` | 管理員 Discord User ID（逗號分隔） |
| `CONCH_OPERATOR_ROLE_IDS` | 操作員 Role ID（逗號分隔） |
| `OPENAI_API_KEY` | OpenAI API Key（用於 /conch-archive 摘要） |

## 設計原則

- 容器管理：純腳本，不跑 LLM
- Thread 封存：使用 OpenAI gpt-4o-mini 產生摘要（無 API key 時 fallback 為純文字截取）
- `restart: always` 確保自身高可用
- 透過 docker.sock 直接操作容器
- 容器管理僅在急診室頻道回應，不主動巡邏
