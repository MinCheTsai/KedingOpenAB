# 🏝️ 比奇堡開發團隊

基於 [OpenAB](https://github.com/openabdev/openab) 的 Discord AI 開發團隊，每個角色都是獨立的 AI agent，擁有自己的個性、職責和工作空間。

## 架構

```
Discord Server: 比奇堡
│
├── AI 角色（OpenAB + kiro-cli）
│   ├── 🧽 海綿寶寶（bob） — 全端工程師
│   ├── ⭐ 派大星（patrick） — 後端工程師
│   ├── 🦑 章魚哥（squidward） — 專案經理 / PM
│   ├── 🐿️ 珊迪（sandy） — 客戶成功經理
│   ├── 🐡 泡芙老師（puff） — Code Review
│   ├── 🐌 小蝸（gary） — 維運助手 / 查詢服務
│   └── 🐚 神奇海螺（magic-conch） — 容器健康監控 & 生命管理
│
├── 獨立服務
│   ├── 🐌 slash-bot — 小蝸的查詢指令服務（/usage、/activity）
│   └── 🐚 magic-conch — 神奇海螺（/conch-status、/conch-logs、/conch-heal）
│
└── Discord 頻道
    ├── 🍔 蟹堡王 — 工作任務交辦
    ├── 🏖️ 比奇堡廣場 — 人類工程師自由交流
    ├── 🗿 復活節島會議室 — 商業洽談 / 新專案討論
    ├── 🧪 珊迪的實驗室 — 技術研究與實驗
    ├── 🐛 海蟲回報站 — Bug 回報
    └── 📺 鯡魚電視台 — 公告通知
```

## 角色說明

| 角色 | 容器名 | 類型 | 說明 |
|------|--------|------|------|
| 🧽 海綿寶寶 | `bob` | OpenAB agent | 全端工程師，主力開發 |
| ⭐ 派大星 | `patrick` | OpenAB agent | 後端工程師 |
| 🦑 章魚哥 | `squidward` | OpenAB agent | 專案經理，任務分配與追蹤 |
| 🐿️ 珊迪 | `sandy` | OpenAB agent | 客戶成功經理 |
| 🐡 泡芙老師 | `puff` | OpenAB agent | Code Review |
| 🐌 小蝸 | `gary` (agent) / `slash-bot` (服務) | OpenAB agent + 獨立服務 | 維運助手，提供 `/usage`、`/activity` 查詢指令 |
| 🐚 神奇海螺 | `magic-conch` | 獨立服務（未來可升級為 agent） | 容器健康監控 & 重啟管理（`/conch-status`、`/conch-logs`、`/conch-heal`） |

## 快速開始

```bash
# 1. 複製環境變數範本
cp .env.example .env
# 編輯 .env 填入 token、channel ID、AWS 認證等

# 2. 啟動
docker compose up -d --build

# 3. 各角色登入 kiro-cli
docker exec -it bob kiro-cli login --use-device-flow
docker exec -it patrick kiro-cli login --use-device-flow

# 4. 登入 gh（如需 git 操作）
docker exec -it bob gh auth login

# 5. 重啟
docker compose restart
```

## 目錄結構

```
bikini-bottom/
├── .env.example              ← 環境變數範本
├── .gitignore
├── Dockerfile                ← 基於官方 OpenAB image + git
├── docker-compose.yml
├── agents/                   ← AI 角色
│   ├── bob/                  ← 🧽 海綿寶寶（全端工程師）
│   ├── patrick/              ← ⭐ 派大星（後端工程師）
│   ├── squidward/            ← 🦑 章魚哥（PM）
│   ├── sandy/                ← 🐿️ 珊迪（客戶成功經理）
│   ├── puff/                 ← 🐡 泡芙老師（Code Review）
│   └── gary/                 ← 🐌 小蝸（維運助手，也是 slash-bot 的人格）
├── shared/                   ← Bot 間共享檔案交換區
│   └── drop/                 ← 扁平交換區（每日自動清空）
├── services/                 ← 獨立服務
│   ├── slash-bot/            ← 🐌 小蝸查詢指令（/usage、/activity）
│   └── magic-conch/          ← 🐚 神奇海螺（容器監控 & 生命管理）
└── docs/
    ├── usage-guide.md        ← 使用指南（給交辦人看）
    ├── new-agent-sop.md      ← 新增角色 SOP
    ├── git-flow-sop.md       ← Git Flow 規範
    ├── discord-channels.md   ← Discord 頻道配置
    └── bot-setup-sop.md      ← Bot 建立 SOP
```

## 常用指令

```bash
# 啟動全部
docker compose up -d --build

# 看特定角色 logs
docker compose logs -f bob

# 重啟特定角色
docker compose restart bob

# 更新 OpenAB 到最新版
docker compose build --pull
docker compose up -d
```

## 文件導讀

| 文件 | 對象 | 內容 |
|------|------|------|
| [docs/usage-guide.md](docs/usage-guide.md) | 交辦人（非工程師） | 怎麼跟 AI 角色互動、流程圖、指令說明（含神奇海螺監控指令） |
| [docs/new-agent-sop.md](docs/new-agent-sop.md) | 維運人員 | 新增 AI 角色的步驟 |
| [docs/bot-setup-sop.md](docs/bot-setup-sop.md) | 維運人員 | Discord Bot 建立與設定 |
| [docs/git-flow-sop.md](docs/git-flow-sop.md) | 開發者 | Git 分支與 PR 規範 |
| [docs/discord-channels.md](docs/discord-channels.md) | 所有人 | Discord 頻道用途說明 |

## 新增角色

參考 [docs/new-agent-sop.md](docs/new-agent-sop.md)。

## 授權

MIT
