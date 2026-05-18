# 新增 Bot SOP

## 一、目錄結構

```
agents/<bot-name>/
├── config.toml                    # Bot 啟動設定
├── .gitconfig                     # Git 身份
├── .kiro/
│   └── steering/                  # Steering 檔案（精簡為原則）
│       ├── personality.md         # 角色設定 + 工作環境（≤30 行）
│       ├── workflow.md            # 工作流程（≤40 行）
│       ├── shared-drive.md        # 共享檔案交換區規則（所有角色）
│       ├── git-flow.md            # Git 規範（開發者角色才需要）
│       ├── mcp-tools.md           # MCP 工具（有用到才加）
│       └── redmine-sop.md         # Redmine 規範（有用到才加）
└── projects/                      # 工作目錄
    ├── _projects.md               # 專案對應表（開發者角色）
    │                              # 或 _status.md（非專案角色如泡芙）
    └── <project-group>/           # 按專案分群組
        ├── specs/                 # 規格文件（read-only 或 read-write）
        └── <repo-name>/          # Git repo + _status.md
```

## 二、config.toml 模板

```toml
[discord]
bot_token = "${DISCORD_BOT_TOKEN_<NAME>}"
allowed_channels = ["${CHANNEL_KRUSTY_KRAB}"]
allow_bot_messages = "mentions"
allow_user_messages = "multibot-mentions"
max_bot_turns = 100

[agent]
command = "kiro-cli"
args = ["acp", "--trust-all-tools"]
working_dir = "/home/agent/projects"
inherit_env = ["GH_TOKEN", "GIT_AUTHOR_NAME", "GIT_COMMITTER_NAME", "GIT_AUTHOR_EMAIL", "GIT_COMMITTER_EMAIL"]

[pool]
max_sessions = 10
session_ttl_hours = 24

[reactions]
enabled = true
remove_after_reply = false

[reactions.emojis]
queued = "👀"
thinking = "🤔"
tool = "🔥"
coding = "🧽"
web = "⚡"
done = "🆗"
error = "😱"

[reactions.timing]
debounce_ms = 700
stall_soft_ms = 10000
stall_hard_ms = 30000
done_hold_ms = 1500
error_hold_ms = 2500
```

## 三、Steering 撰寫原則

### Token 預算

| 檔案 | 目標行數 | 說明 |
|------|----------|------|
| personality.md | ≤ 30 行 | 身份、個性、口頭禪、工作環境 |
| workflow.md | ≤ 40 行 | 核心流程，不含細節 SOP |
| git-flow.md | ≤ 80 行 | 分支策略、PR 流程 |
| mcp-tools.md | ≤ 20 行 | 工具清單 + 關鍵注意事項 |
| redmine-sop.md | ≤ 60 行 | 狀態對照 + 操作規則 |
| **合計** | **≤ 230 行** | 約 2000 tokens |

### 精簡原則

- 不寫範例（bot 會自己推斷）
- 不重複（多個檔案不要說同一件事）
- 用表格取代長段落
- 只寫「必須遵守」的規則，不寫「最好這樣做」的建議

## 四、`_projects.md` 模板

```markdown
# 我負責的專案

| 專案 | 路徑 | Repos | Specs 路徑 | 關鍵字 |
|------|------|-------|-----------|--------|

## 使用方式

1. 收到任務時，先讀這個檔案
2. 從訊息內容比對「關鍵字」欄位，確定是哪個專案
3. 進入該專案的路徑，讀 specs/ 和各 repo 的 _status.md
4. 如果比對不到任何專案 → 問對方是哪個專案
5. 如果是全新專案 → clone repo 後，在這裡新增一筆紀錄
```

## 五、`_status.md` 模板

```markdown
# <repo-name> 開發狀態

## 進行中
（無）

## 最近完成（最多 5 筆）

## 待確認

## 封存
超過 5 筆的完成紀錄在 _archive.md
```

## 五之一、Cronjob 設定注意事項

`cronjob.toml` **不支援** `${...}` 環境變數語法。channel 必須直接填入 Discord channel ID 數字字串。

```toml
# ❌ 錯誤 — cron 模組無法解析環境變數
channel = "${CHANNEL_KRUSTY_KRAB}"

# ✅ 正確 — 直接填入 channel ID
channel = "1492090122257170526"
```

常用 Channel ID 對照（見 `.env`）：

| 變數名 | Channel ID | 說明 |
|--------|-----------|------|
| CHANNEL_KRUSTY_KRAB | 1492090122257170526 | 蟹堡王（工作） |
| CHANNEL_PLAZA | 1503940169252999198 | 廣場（閒聊） |
| CHANNEL_MEETING | 1503703338800382002 | 會議室 |

> 注意：`config.toml` 中的 `allowed_channels` **可以**使用 `${...}` 語法（由 OpenAB 主程式解析），但 `cronjob.toml` 由 cron 模組獨立解析，不支援環境變數。

## 六、新增 Bot 步驟

1. 在 `.env` 加入 `DISCORD_BOT_TOKEN_<NAME>=...`
2. 建立 `agents/<bot-name>/` 目錄結構（參考第一節）
3. 撰寫 `config.toml`（參考第二節模板）
4. 撰寫 `.gitconfig`
5. 撰寫 steering 檔案（遵守第三節預算）
6. 加入 `shared-drive.md` steering（參考第八節）
7. 在 `docker-compose.yml` 加入 `- ./shared:/shared` volume
8. 建立 `projects/` 初始結構
9. 在 Discord 建立 Bot Application + 取得 Token
10. 設定 Bot 頭像（在 Discord Developer Portal → Bot → 上傳 Avatar）
11. 更新神奇海螺的容器對應（`services/magic-conch/bot.py` 的 `ROLE_MAP` + `MANAGED_CONTAINERS`）
12. 部署/重啟 OpenAB

## 七、角色類型對照

| 角色類型 | 需要的 steering | projects 結構 |
|---------|----------------|---------------|
| 開發者（bob, patrick） | personality + workflow + git-flow + mcp-tools + redmine-sop | _projects.md + 專案群組/repos |
| Reviewer（puff） | personality + workflow + review-rules + git-tools | _status.md（無專案群組） |
| PM（squidward） | personality + workflow + mcp-tools + redmine-sop | _projects.md + 專案群組/specs |
| 客戶成功經理（sandy） | personality + workflow | _projects.md + 實驗紀錄 |
| 工具型 Bot（conch, gary） | 無（非 AI agent） | README.md + spec.md |

## 七之一、容器名稱對應表（神奇海螺用）

新增角色時，需同步更新 `services/magic-conch/bot.py` 中的 `ROLE_MAP` 和 `MANAGED_CONTAINERS`，讓神奇海螺能管理新容器。

| 暱稱 | 容器名稱 | 類型 |
|------|---------|------|
| 海綿寶寶 / bob | bob | AI agent |
| 派大星 / patrick | patrick | AI agent |
| 章魚哥 / squidward | squidward | AI agent |
| 珊迪 / sandy | sandy | AI agent |
| 泡芙老師 / puff | puff | AI agent |
| 小蝸 / gary | slash-bot | 工具 Bot |
| 企微 / wecom | wecom-bot | AI agent |
| gateway | gateway | 服務 |

## 八、共享檔案交換區

所有 bot（wecom-bot 除外）掛載 `./shared:/shared`，用於 bot 之間交換檔案。

### 結構
```
/shared/
├── README.md    # 說明文件
└── drop/        # 扁平交換區，每日自動清空
```

### 檔名格式
```
<寄件人>_<簡述>_v<版本號>.<副檔名>
```

### 管理機制
- 每日定時清空 `drop/` 目錄
- 版本號遞增避免覆蓋（v1 → v2 → v3）
- 每個 bot 的 steering 中有 `shared-drive.md` 說明使用規則

### 新增 bot 時
- 在 docker-compose 加入 `- ./shared:/shared` volume
- 在 steering 目錄加入 `shared-drive.md`

---

## 九、頻道行為設定

每個角色的 steering 中應包含「頻道行為」表格，定義該角色在不同頻道的回應風格：

- **蟹堡王**：工作模式（任務交辦、進度回報）
- **廣場**：閒聊模式（輕鬆聊天，不限於職責範圍）
- **會議室**：正式模式（需求討論、規格產出）
- **實驗室**：實驗模式（POC 驗證、技術探索）
- **海蟲回報站**：Bug 處理模式
