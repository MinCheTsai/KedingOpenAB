# 🧽 Redmine MCP POC 計畫

> 目標：讓比奇堡的 AI agent 能透過 MCP 連接公司 Redmine，讀取 issue、回覆留言、更新狀態。
> 第一階段以海綿寶寶解數學題作為 POC 驗證。

---

## 階段一：環境準備

### 1.1 Redmine 帳號建立

- [x] 在公司 Redmine 建立「海綿寶寶」本地帳號（不依賴 AD/LDAP）
- [x] 取得海綿寶寶的 API Key（我的帳號 → API 存取金鑰）
- [x] 確認海綿寶寶帳號有權限：讀取專案、讀取/更新 issue、新增留言（已透過 API 驗證）
- [ ] （未來）建立「派大星」本地帳號 + API Key

### 1.2 收集必要參數

需要提供的參數：

| 參數 | 說明 | 狀態 |
|------|------|------|
| `REDMINE_URL` | 公司 Redmine 網址（例如 `https://redmine.company.com`） | ⬜ 待提供 |
| `REDMINE_API_KEY_BOB` | 海綿寶寶的 Redmine API Key | ⬜ 待提供 |

### 1.3 建立測試 Issue

- [x] 在 Redmine 建立一個測試 issue
  - 標題：「Math Test for Agent」
  - 描述：「請計算：17 × 23 = ?」
  - Issue #1221，專案：Agent測試專案（ID: 9）
  - 已分配給 SpongeBob

### 1.4 確認 Redmine 狀態值

- [x] 確認公司 Redmine 的 issue 狀態清單（特別是「已解決」對應的名稱）
  - Redmine 管理 → Issue 狀態，或透過 API: `GET /issue_statuses.json`
  - ✅ 已確認，沒有「已解決」，POC 先用「已完成」（ID: 3）
  - ⚠️ 備註：正式使用時需遵守團隊的狀態流轉規則，規則之後補充
  - 完整狀態清單：尚未開發(1)、開發中(2)、review(9)、測試中(8)、已完成(3)、暫停(7)、回饋(4, closed)、關閉(5)

---

## 階段二：MCP Server 設定

### 2.1 選定 MCP Server 方案

- [x] 研究 runekaagaard/mcp-redmine（SSE transport）
  - ❌ SSE transport 有 DNS rebinding protection，Docker 容器間連線回 421
  - 詳見 `docs/mcp-redmine-setup.md`（已標記過時，保留作歷史參考）
- [x] 改用 [jztan/redmine-mcp-server](https://pypi.org/project/redmine-mcp-server/)（HTTP Streamable）
  - ✅ HTTP Streamable transport，無 DNS rebinding 問題
  - 21 個專用工具（issue CRUD、wiki、time tracking、搜尋、專案摘要）
  - Redmine 4.1 相容性已驗證

### 2.2 部署 MCP Server

- [x] 撰寫部署指南：`docs/mcp-redmine-deploy.md`
- [x] 本機 Docker 部署測試通過（POC 階段）
- [ ] 由工程師依部署指南部署到 MCP 服務器（正式環境）

### 2.3 設定 MCP Client Config

- [x] 為海綿寶寶建立 MCP config：`agents/bob/.kiro/settings/mcp.json`
- [ ] （未來）為派大星建立 MCP config：`agents/patrick/.kiro/settings/mcp.json`

設計原則：
- 每個角色各自一份 `mcp.json`，指向同一個 MCP server（共用 API Key）或各自的 instance
- MCP server 使用 HTTP Streamable transport，角色用內網 IP 連線
- `autoApprove` 必須設定，kiro-cli ACP 模式下才能自動執行工具
- 連線設定參考：`docs/mcp-config-reference.md`

---

## 階段三：驗證連線

### 3.1 基本讀取測試

- [x] 透過 MCP 呼叫 list projects — 確認至少回傳 1 個專案
- [x] 透過 MCP 呼叫 list issues — 確認至少回傳 1 個 issue
- [x] 透過 MCP 讀取測試 issue 的詳細內容

### 3.2 寫入測試

- [x] 透過 MCP 對測試 issue 新增一則留言
- [x] 透過 MCP 更新測試 issue 的狀態
- [x] 到 Redmine 網頁確認留言和狀態都正確顯示
- ✅ 海綿寶寶在 Discord 上成功透過 MCP 讀取 issue #1221 並回覆留言

---

## 階段四：Agent 行為調教（steering 驅動）

> 原計畫為撰寫 Python 腳本，但實際驗證後發現透過 steering 驅動 kiro-cli 即可完成，
> 不需要額外的腳本。改為透過 steering-lab 實驗框架迭代調教。

### 4.1 建立 steering-lab 實驗框架

- [x] 建立 `steering-lab/` 目錄結構（facets、profiles、experiments）
- [x] 將海綿寶寶現有 steering 搬入 facets 作為 v1 基線
- [x] 建立 EXP-001 實驗組合（exp-redmine）

### 4.2 EXP-001：Redmine 自動任務處理

- [x] 海綿寶寶成功讀取 issue 並回覆留言
- [ ] 調教任務處理順序（接收 issue 編號後的步驟執行順序）
- [ ] 調教留言格式和內容品質
- [ ] 需請開發主管提供 Redmine 工作流程 SOP，明訂狀態轉換規則
- ⚠️ 需觀察海綿寶寶的 Discord 對話紀錄來迭代 workflow steering

### 4.3 驗收標準

- [ ] 海綿寶寶能完整執行：讀取 → 開發中 → 處理 → 留言回報 → 已完成
- [ ] 留言格式符合預期
- [ ] 狀態轉換符合團隊 SOP

---

## 階段五：整合與文件

### 5.1 MCP Server 正式部署

- [ ] 工程師依 `docs/mcp-redmine-deploy.md` 部署到 MCP 服務器
- [ ] 角色 `mcp.json` 改用正式環境的內網 IP
- [ ] 移除 docker-compose 的 `extra_hosts`（不再需要 host.docker.internal）

### 5.2 擴展到其他角色

- [ ] 派大星的 Redmine 帳號 + API Key
- [ ] 派大星的 MCP config
- [ ] 測試派大星也能獨立操作 Redmine

### 5.3 文件更新

- [x] 撰寫 MCP 部署指南：`docs/mcp-redmine-deploy.md`
- [x] 撰寫 MCP 連線設定參考：`docs/mcp-config-reference.md`
- [ ] 更新 README.md 加入 Redmine MCP 相關說明

### 5.4 Redmine 升級評估

- [ ] 研究 Redmine 4.1 → 6.1 升級路徑（OAuth2 支援需 6.1+）
- [ ] 升級後可改用 OAuth2 模式，每個角色動態帶入自己的 token，不需多 instance
- ⚠️ 現階段只能用 legacy 模式（一個 instance 一組 API Key），多角色需部署多個 instance

---

## 備註

- Redmine MCP Server 使用 [redmine-mcp-server](https://pypi.org/project/redmine-mcp-server/)（HTTP Streamable transport）
- 公司 Redmine 版本為 4.1，已驗證相容
- Agent 使用 Redmine 本地帳號 + API Key 認證，不依賴 AD/LDAP
- 每個角色各自一組 API Key，確保 Redmine 上的操作紀錄能區分身份
- POC 階段 MCP server 本機部署（`tmp/redmine-mcp/`，不進 git），正式環境由工程師部署到 MCP 服務器

## 踩坑紀錄：kiro-cli 連接 MCP 的必要條件

### 1. MCP config（`~/.kiro/settings/mcp.json`）

```json
{
  "mcpServers": {
    "<server-name>": {
      "url": "http://<host>:<port>/<path>",
      "headers": {
        "Authorization": "Bearer <token>"
      }
    }
  }
}
```

### 2. Agent config — 不要自訂

不要建立 `~/.kiro/agents/kiro_default.json`。built-in 的 `kiro_default` 有 `tools: ["*"]` 會自動包含所有 MCP tools，
而且會自動讀取 steering 檔案（personality.md 等）。自訂的會覆蓋 built-in，導致角色失去個性和 steering。

### 3. Steering 裡明確告知角色有 MCP 工具

kiro-cli ACP 模式的 MCP 是 lazy initialization，角色不會主動知道自己有 MCP 工具。
解法：在 `~/.kiro/steering/mcp-tools.md` 裡列出所有可用的 MCP 工具和使用方式。
這樣角色被問到時就會知道自己有這些工具，也會主動使用。

### 4. MCP server 必須先啟動

MCP server 必須在角色的 container 啟動前就已經在跑。

### 5. DNS rebinding protection（已透過換方案解決）

舊方案 runekaagaard/mcp-redmine 使用 MCP Python SDK 的 SSE transport，
預設開啟 DNS rebinding protection，只允許 `localhost`、`127.0.0.1`、`[::1]` 作為 Host header。
Docker 容器間連線會被 `421 Invalid Host header` 擋住。

解法：改用 jztan/redmine-mcp-server，使用 HTTP Streamable transport，無此問題。

### 6. Docker 容器連 host 服務

容器內的 `localhost` 是容器自己，不是 host 機器。
要連 host 上的服務（如本機部署的 MCP server），需要：
- 在 docker-compose 加 `extra_hosts: ["host.docker.internal:host-gateway"]`
- `mcp.json` 使用 `http://host.docker.internal:<port>/mcp`
- 未來 MCP server 部署到遠端主機後，直接用內網 IP，不需要 extra_hosts

---

## 🔴 目前未完成項目（截至 2026-04-16 下午）

### 需要你（人類）處理
1. ~~**提供 Redmine 開發流程 SOP**~~ ✅ 已提供，已轉為 steering facet
2. **開 PR 合併** — 分支 `kiro_20260416_redmine-mcp-poc` 已推，待 review 後合併
3. **請工程師部署 Redmine MCP 到 MCP 服務器** — 依 `docs/mcp-redmine-deploy.md`
4. **決定多 instance 部署方案** — 海綿寶寶和派大星各自一組 API Key，需各自一個 MCP instance

### 需要 Kiro 處理
5. ~~**EXP-001 調教**~~ ✅ 已完成多輪測試迭代：加入 redmine-sop、錯誤處理、狀態 ID 對照、確認理解流程、Discord 回覆精簡、Redmine 留言專業化、steering token 優化
6. **MCP server 遠端部署後更新 mcp.json** — 工程師部署完成後，改用正式環境的內網 IP，移除 extra_hosts
7. **派大星的 Redmine 帳號 + MCP config** — 待派大星帳號建立後設定

### 下一個 POC：Git Flow
8. **Git Flow SOP** — 所有涉及程式碼修改的完整流程（獨立於 Redmine）：
   - [x] 撰寫 Git Flow SOP 文件：`docs/git-flow-sop.md`
   - [x] 建立 git-flow steering facet：`steering-lab/facets/shared/git-flow/v1-standard.md`
   - [x] 建立整合 workflow facet：`steering-lab/facets/bob/workflow/exp-git-flow.md`
   - [x] 建立實驗組合 profile：`steering-lab/profiles/bob/exp-git-flow.txt`
   - [x] Dockerfile 加入 `gh`（GitHub CLI）
   - [x] GitHub 認證改用 `GH_TOKEN` 環境變數（共用 PAT，方案 B）
   - [ ] 人類提供 GitHub PAT，填入 `.env` 的 `GH_TOKEN`
   - [ ] 重建 image：`docker compose build --pull`
   - [ ] 套用 exp-git-flow 組合：`./steering-lab/apply.sh bob exp-git-flow`
   - [ ] 重啟容器測試完整流程
9. **Redmine + Git 整合** — Redmine issue 狀態轉換與 git flow 階段的對應關係
   - [x] 已在 `docs/git-flow-sop.md` 第六節說明搭配方式

### 未來規劃
10. **Redmine 升級 6.1 評估** — OAuth2 支援，解決多帳號需多 instance 的問題
11. **多角色協作** — 蟹老闆分配 issue、海綿寶寶前端、派大星後端（仍在探索階段）
12. **更新 README.md** — 加入 Redmine MCP 相關說明
13. **Discord Channel 情境切換** — 利用 channel ID 作為 Agent 的工作場景切換機制：
    - 不同 channel 對應不同專案/情境，Agent 自動套用對應規範
    - 需建立 channel ID → 專案的對照表（寫在 steering 裡）
    - 可搭配 Redmine 專案 ID、git repo、coding style 等專案級設定
    - 多角色在同一 channel 時可自然協作（共享專案上下文）
    - 限制：Agent 只能看到 channel ID，看不到名稱；新增 channel 需同步更新 steering 和 config.toml
10. **更新 README.md** — 加入 Redmine MCP 相關說明

---

## 進度追蹤

| 日期 | 完成項目 | 備註 |
|------|----------|------|
| 2025/04/15 | 建立 TODO.md | 計畫啟動 |
| 2025/04/15 | 收到 REDMINE_URL 和海綿寶寶 API Key | 已寫入 .env，同步更新 .env.example |
| 2025/04/15 | 完成 mcp-redmine 研究 | 確認所有功能都支援，撰寫維運文件 `docs/mcp-redmine-setup.md` |
| 2025/04/15 | MCP Server 連線成功 | Kiro IDE 透過 SSE 連上 mcp-redmine，成功讀取 issue #1221 和 statuses |
| 2025/04/15 | 海綿寶寶 MCP 連線成功 | 用 hrs-mcp 驗證 kiro-cli ACP 模式可連 MCP。關鍵：不需自訂 agent config（用 built-in），需在 steering 加 mcp-tools.md |
| 2025/04/15 | 待完成：回公司內網後用 redmine MCP 完成 POC | mcp.json 已改回 redmine，steering 已加 mcp-tools.md |
| 2026/04/16 | 換用 redmine-mcp-server (jztan) | 舊版 runekaagaard/mcp-redmine 的 SSE transport 有 DNS rebinding 問題（421），改用 HTTP Streamable 的 redmine-mcp-server，21 個專用工具 |
| 2026/04/16 | 海綿寶寶 Redmine MCP 連線成功 | 透過 host.docker.internal 連上 redmine-mcp-server，成功讀取 issue #1221 並回覆留言 |
| 2026/04/16 | 建立 steering-lab 實驗框架 | facets + profiles 管理 steering 版本，apply.sh 切換組合 |
| 2026/04/16 | 建立 Redmine MCP 部署文件 | `docs/mcp-redmine-deploy.md` |
| | | |
