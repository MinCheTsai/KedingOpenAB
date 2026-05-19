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
│       ├── git-flow.md            # Git 規範（開發者角色才需要）
│       ├── mcp-tools.md           # MCP 工具（有用到才加）
│       └── redmine-sop.md         # Redmine 規範（有用到才加）
│       # 以下為共用 steering（容器啟動時自動 symlink 自 /shared/steering/）
│       # rules.md, team-members.md, shared-drive.md, channel-handoff.md
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
allowed_channels = ["${CHANNEL_KRUSTY_KRAB}", "${CHANNEL_PLAZA}"]
allow_bot_messages = "mentions"
allow_user_messages = "mentions"
allowed_role_ids = ["1504289434122588200", "<個人身分組ID>"]
max_bot_turns = 100

[agent]
command = "kiro-cli"
args = ["acp", "--trust-all-tools"]
working_dir = "/home/agent/projects"
env = { KIRO_API_KEY = "${KIRO_API_KEY}" }
inherit_env = ["GH_TOKEN", "GIT_AUTHOR_NAME", "GIT_COMMITTER_NAME", "GIT_AUTHOR_EMAIL", "GIT_COMMITTER_EMAIL", "KIRO_API_KEY"]

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
coding = "<角色代表 emoji>"
web = "⚡"
done = "🆗"
error = "😱"

[reactions.timing]
debounce_ms = 700
stall_soft_ms = 10000
stall_hard_ms = 30000
done_hold_ms = 1500
error_hold_ms = 2500

[cron]
usercron_enabled = true
usercron_path = "cronjob.toml"
```

### config.toml 重點說明

| 設定 | 說明 |
|------|------|
| `allow_user_messages = "mentions"` | 必須被 @mention 才回應，避免 thread 首次 mention 不回應的問題 |
| `allow_bot_messages = "mentions"` | bot 間互相 mention 才觸發，防止無限迴圈 |
| `allowed_role_ids` | 身分組 mention 觸發，等同直接 @mention bot |

### allowed_role_ids 設定規則

每個 bot 的 `allowed_role_ids` 應包含：
1. 該 bot 所屬的**群組身分組**（mention 群組時觸發）
2. 該 bot 的**個人身分組**（mention 個人身分組時觸發）

**不要加入**人類專屬的身分組（科定主管、科定人類、科定工程師）。

### 身分組對照表

| 身分組名稱 | Role ID | 觸發對象 |
|-----------|---------|---------|
| 比奇堡小夥伴們 | `1504289434122588200` | 全員 |
| 比奇堡開發組 | `1506122390751678484` | 海綿、派大星、泡芙、章魚哥 |
| 比奇堡專案組 | `1506130693812391946` | 章魚哥、珊迪 |
| 海綿寶寶 | `1504316850316509215` | 海綿 |
| 派大星 | `1496024872222986313` | 派大星 |
| 泡芙老師 | `1503577722901893182` | 泡芙 |
| 章魚哥 | `1503699904176853033` | 章魚哥 |
| 珊迪 | `1504348022803402835` | 珊迪 |
| 科定主管 | `1505819441496068106` | ❌ 不觸發 bot |
| 科定人類 | `1504289843264360528` | ❌ 不觸發 bot |
| 科定工程師 | `1506130970544308305` | ❌ 不觸發 bot |

### Discord 身分組設定注意

身分組必須在 Discord 伺服器設定中開啟「允許任何人 @mention 這個身分組」，否則 Discord 不會在訊息中帶上 `mention_roles`，OpenAB 就收不到。

## 三、共用 Steering 機制

共用 steering 文件放在 `shared/steering/`，容器啟動時由 `entrypoint-wrapper.sh` 自動 symlink 到 `/home/agent/.kiro/steering/`。

### 共用文件

| 文件 | 用途 |
|------|------|
| `rules.md` | 鐵律（mention 檢查、禁止 commit 狀態檔、時區、不合併 PR、不 force push） |
| `team-members.md` | 團隊成員 mention 表（唯一來源） |
| `shared-drive.md` | 共享檔案交換區規則 |
| `channel-handoff.md` | 跨頻道交接協議 |

### 修改共用規則

只需修改 `shared/steering/` 裡的文件，重啟容器後所有 bot 自動生效。不需要逐一修改各 agent 的 steering。

### 新增 bot 時

不需要手動建立共用 steering 文件，容器啟動時會自動 symlink。

## 四、Steering 撰寫原則

### Token 預算

| 檔案 | 目標行數 | 說明 |
|------|----------|------|
| personality.md | ≤ 30 行 | 身份、個性、口頭禪、工作環境、時區 |
| workflow.md | ≤ 40 行 | 核心流程，不含細節 SOP |
| git-flow.md | ≤ 80 行 | 分支策略、PR 流程、禁止 commit 清單 |
| mcp-tools.md | ≤ 20 行 | 工具清單 + 關鍵注意事項 |
| redmine-sop.md | ≤ 60 行 | 狀態對照 + 操作規則 |
| **合計** | **≤ 230 行** | 約 2000 tokens |

### 精簡原則

- 不寫範例（bot 會自己推斷）
- 不重複（多個檔案不要說同一件事）
- 用表格取代長段落
- 只寫「必須遵守」的規則，不寫「最好這樣做」的建議
- 團隊成員表、共用規則不要寫在個別 steering 裡（用共用 steering）

### personality.md 必須包含

- 時區：`Asia/Taipei (UTC+8)，所有時間相關的回覆以台灣時間為準`

### git-flow.md 必須包含（開發者角色）

禁止 commit 的檔案清單：
- `_status.md`、`_archive.md`、`_projects.md`、`.env`

## 五、`_projects.md` 模板

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

## 六、`_status.md` 模板

```markdown
# <repo-name> 開發狀態

## 進行中
（無）

## 最近完成（最多 5 筆）

## 待確認

## 封存
超過 5 筆的完成紀錄在 _archive.md
```

## 七、Cronjob 設定注意事項

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

## 八、新增 Bot 步驟

1. 在 Discord Developer Portal 建立 Bot Application + 取得 Token
2. 在 Discord 伺服器建立該 bot 的個人身分組，並加入相關群組身分組
3. 確認身分組開啟「允許任何人 @mention」
4. 在 `.env` 加入 `DISCORD_BOT_TOKEN_<NAME>=...` 和 `KIRO_API_KEY_<NAME>=...`
5. 建立 `agents/<bot-name>/` 目錄結構（參考第一節）
6. 撰寫 `config.toml`（參考第二節模板，設定 `allowed_role_ids`）
7. 撰寫 `.gitconfig`
8. 撰寫 steering 檔案（遵守第四節預算，personality.md 必須含時區）
9. 在 `docker-compose.yml` 加入服務定義（含 `- ./shared:/shared` volume）
10. 建立 `projects/` 初始結構
11. 設定 Bot 頭像（在 Discord Developer Portal → Bot → 上傳 Avatar）
12. 更新 `shared/steering/team-members.md`（加入新成員）
13. 更新神奇海螺的容器對應（`services/magic-conch/bot.py` 的 `ROLE_MAP` + `MANAGED_CONTAINERS`）
14. `docker compose build --pull && docker compose up -d`

## 九、角色類型對照

| 角色類型 | 需要的 steering | projects 結構 |
|---------|----------------|---------------|
| 開發者（bob, patrick） | personality + workflow + git-flow + mcp-tools + redmine-sop | _projects.md + 專案群組/repos |
| Reviewer（puff） | personality + workflow + review-rules + git-tools | _status.md（無專案群組） |
| PM（squidward） | personality + workflow + mcp-tools + redmine-sop | _projects.md + 專案群組/specs |
| 客戶成功經理（sandy） | personality + workflow | _projects.md + 實驗紀錄 |
| 工具型 Bot（conch, gary） | 無（非 AI agent） | README.md + spec.md |

## 十、容器名稱對應表（神奇海螺用）

新增角色時，需同步更新 `services/magic-conch/bot.py` 中的 `ROLE_MAP` 和 `MANAGED_CONTAINERS`。

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

## 十一、共享檔案交換區

所有 bot（wecom-bot 除外）掛載 `./shared:/shared`。

### 結構
```
/shared/
├── steering/    # 共用 steering 文件（自動 symlink 到各 bot）
├── docs/        # 共用流程文件
└── drop/        # 扁平交換區，每日自動清空
```

### 檔名格式（drop/）
```
<寄件人>_<簡述>_v<版本號>.<副檔名>
```

## 十二、頻道行為設定

每個角色的 steering 中應包含「頻道行為」表格，定義該角色在不同頻道的回應風格：

- **蟹堡王**：工作模式（任務交辦、進度回報）
- **廣場**：閒聊模式（輕鬆聊天，不限於職責範圍）
- **會議室**：正式模式（需求討論、規格產出）
- **實驗室**：實驗模式（POC 驗證、技術探索）
- **海蟲回報站**：Bug 處理模式

## 十三、OpenAB 版本管理

- Dockerfile 使用**指定版本** tag（如 `FROM ghcr.io/openabdev/openab:0.8.3-beta.5`）
- 不使用 `latest` tag（`latest` 只在 stable release 時更新，beta 不會推）
- 更新時參考 [OpenAB Releases](https://github.com/openabdev/openab/releases)，無論 beta 或 stable 都以最新版本更新
- 本地原始碼參考放在 `refs/openab/`
- 詳細更新步驟見 `docs/openab-upgrade-sop.md`
