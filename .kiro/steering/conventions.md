---
inclusion: manual
---

# 開發慣例

## 語言

- 所有文件、註解、commit message 使用繁體中文
- 角色的 steering 檔案全程繁體中文，不使用英文
- 程式碼中的變數名和技術術語可以用英文

## 角色管理

- 每個角色一個獨立目錄在 `agents/<alias>/`
- 角色別名使用英文小寫（bob, patrick, gary, krabs, squidward, sandy, plankton）
- 新增角色遵循 `docs/new-agent-sop.md`
- 角色的 config.toml 中使用 `${ENV_VAR}` 引用環境變數，實際值放 `.env`

## Docker

- AI 角色使用根目錄的 `Dockerfile`（基於官方 OpenAB image）
- 獨立服務各自有自己的 `Dockerfile` 在 `services/<name>/`
- 不要把 token 或密鑰寫死在任何檔案中，一律用環境變數

## 環境變數命名

- Bot token：`DISCORD_BOT_TOKEN_<ALIAS>`（例如 `DISCORD_BOT_TOKEN_BOB`）
- Channel ID：`CHANNEL_<NAME>`（例如 `CHANNEL_GENERAL`）
- 新增變數時同步更新 `.env.example`

## Git

- 分支策略：`master`（正式）+ `develop`（開發），一般開發對 `develop` 開 PR，hotfix 同時對 `master` 和 `develop` 開 PR
- 分支命名格式：`<角色別名>_<YYYYMMDD>_<簡短描述>`
  - Kiro IDE：`kiro_<YYYYMMDD>_<描述>`
  - Agent：`<別名>_<YYYYMMDD>_<描述>`（例如 `bob_20260416_fix_null_check`）
- 簡短描述使用英文小寫，多個單字用 `_` 連接
- commit message 使用繁體中文，格式：`feat/fix/chore/docs: 簡短描述`，可附多行說明
- PR 標題與分支名相同
- 不直接 push 到 master 或 develop
- Agent 不可自行合併 PR，由主管合併
- GitHub 認證使用共用 `GH_TOKEN`（PAT），透過環境變數注入
- 完整流程參考 `docs/git-flow-sop.md`
