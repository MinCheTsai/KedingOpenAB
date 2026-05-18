# 🐚 神奇海螺 (Magic Conch)

輕量容器管理 Bot，以 Slash Command 操作，不走 OpenAB / kiro-cli。

## 類型

腳本型 Discord Bot（Python + discord.py + docker SDK）

## 職責

- 容器生命管理（重啟 / 停止 / 診斷）
- 狀態查詢（log / rollcall）

## 使用頻道

僅限「🏥 急診室」頻道（ID: 1505752303624392755）

## 程式碼位置

`services/magic-conch/`

## 指令集

| 指令 | 功能 | 權限 |
|------|------|------|
| `/conch-status [target]` | 查看狀態 | 所有人 |
| `/conch-heal [target]` | 重啟容器 | 操作員 |
| `/conch-kill [target]` | 停止容器 | 管理員 |
| `/conch-diagnose [target]` | 健康診斷 | 所有人 |
| `/conch-logs [target] [lines]` | 查看 log | 所有人 |
| `/conch-rollcall` | 全員點名 | 所有人 |
| `/conch-restart-all [confirm]` | 全員重啟 | 管理員 |

## 環境變數

| 變數 | 說明 |
|------|------|
| `DISCORD_BOT_TOKEN_CONCH` | Bot Token |
| `DISCORD_GUILD_ID` | Guild ID（共用） |
| `CONCH_CHANNEL_ID` | 限定使用頻道（急診室） |
| `CONCH_ADMIN_IDS` | 管理員 Discord User ID（逗號分隔） |
| `CONCH_OPERATOR_ROLE_IDS` | 操作員 Role ID（逗號分隔） |

## 設計原則

- 不跑 LLM，純腳本
- `restart: always` 確保自身高可用
- 透過 docker.sock 直接操作容器
- 僅在急診室頻道回應，不主動巡邏
