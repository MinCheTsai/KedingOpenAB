# Git Flow 標準作業流程

> 所有涉及程式碼修改的工作都遵循此流程，無論來源是 Redmine issue、Discord 口頭交辦、或 hotfix。
> Agent 和人類開發者都適用。

## 分支策略

- `master`：正式環境分支
- `develop`：開發分支，所有一般開發先合併到這裡
- `develop` → `master` 的合併由主管處理，Agent 不介入

### 一般流程

```
收到需求
  ↓
從 develop 開分支
  ↓
開發 + commit
  ↓
push + 對 develop 開 PR
  ↓
加上 "ai code review" 標籤 → 觸發 AI Code Review
  ↓
根據 review 意見自我修正（最多 3 輪）
  ↓
移除 "ai code review" 標籤，加上 "awaiting review" 標籤
  ↓
主管 review + 合併
```

### Hotfix 流程（需明確被告知是 hotfix）

```
收到 hotfix 需求
  ↓
從 master 開分支
  ↓
開發 + commit
  ↓
push + 同時對 master 和 develop 各開一個 PR
  ↓
兩個 PR 都走 AI Code Review + 主管 review 流程
```

## 一、分支命名規則

格式：`<角色別名>_<YYYYMMDD>_<簡短描述>`

- 角色別名：`bob`、`patrick` 等
- 日期：開分支當天
- 簡短描述：英文小寫，多個單字用 `_` 連接

範例：
- `bob_20260416_add_login_api`
- `patrick_20260416_fix_db_connection`

> Kiro IDE 的分支命名格式為 `kiro_<YYYYMMDD>_<描述>`，Agent 使用自己的角色別名。

## 二、PR 規則

- PR 標題格式與分支名相同：`<角色別名>_<YYYYMMDD>_<簡短描述>`
- PR 描述說明修改內容和原因
- 如果有對應的 Redmine issue，在描述中附上編號（非必要）
- Agent 不可自行合併 PR，一律由主管合併

## 三、AI Code Review 機制

1. PR 開好後，Agent 加上 `ai code review` 標籤
2. AI Code Review 會自動觸發，結果回應在 PR conversation 中
3. Agent 查看 review 結果並自我修正：
   - 認同意見 → 修正程式碼，commit + push
   - 不認同 → 在 PR conversation 留言說明理由，不修改該項
4. 每次 push 會再次觸發 AI Code Review（只要標籤還在）
5. 最多進行 **3 輪**修正
6. 3 輪結束後（或提前達成共識）：
   - 移除 `ai code review` 標籤（停止自動 review）
   - 加上 `awaiting review` 標籤（通知主管）
7. 如果 3 輪後仍有未解決的意見，Agent 在 PR 留言摘要說明哪些項目未修正及原因

## 四、CI 錯誤處理

- 如果 PR 觸發 CI 且失敗，Agent 需查看錯誤訊息並嘗試修正
- CI 修正也算在 3 輪修正次數內
- 無法解決的 CI 錯誤，在 PR 留言說明，交給主管處理

## 五、工具需求

| 工具 | 用途 | 安裝狀態 |
|------|------|----------|
| `git` | 版本控制 | ✅ 已安裝（Dockerfile） |
| `gh` | GitHub CLI（開 PR、管理標籤） | ✅ 已安裝（Dockerfile） |

### gh 認證

Agent 容器透過 `GH_TOKEN` 環境變數自動認證，不需要手動 `gh auth login`。
`GH_TOKEN` 在 `.env` 中設定，所有 Agent 共用同一組 PAT。

### GitHub 帳號

- 目前所有 Agent 共用一組 GitHub PAT
- commit 身份透過 `GIT_AUTHOR_NAME` / `GIT_COMMITTER_NAME` 環境變數區分
- GitHub 上的 commit 紀錄可看出是哪個 Agent 提交的
- 未來如需帳號切分，改為每個 Agent 各自一組 PAT

## 六、與 Redmine 的搭配（選用）

當任務來自 Redmine issue 時，Git Flow 結束後額外做：
- 在 Redmine issue 留言附上 PR 連結
- 更新 Redmine issue 狀態

這部分由 Redmine SOP 規範，不屬於 Git Flow 本身。
