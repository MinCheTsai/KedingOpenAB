# 工作流程規範

## 工作日誌

- 你的記憶不會跨對話保留，必須依賴檔案記住事情
- 維護 `/home/agent/projects/WORKLOG.md`
- 每次工作前先讀取，完成後在最上方新增紀錄：

```
## YYYY-MM-DD 簡短標題
- 做了什麼
- 目前狀態
- 待辦事項
```

- 只保留最近 10 筆，超過的移到 `WORKLOG-archive.md` 最上方

## 交接原則

- 假設每次對話都是全新的開始
- 重要資訊寫進檔案，不要只存在對話裡

## Discord 回覆原則

- 工作日誌讀取/更新、Redmine 留言回報、狀態更新都是背景作業，不需要在 Discord 中說明
- 只講重點：任務結果、需要確認的事項、遇到的問題
- 不要逐步描述過程，做完再講結果

## 程式碼修改流程（Git Flow）

所有涉及程式碼修改的工作，無論來源（Redmine、Discord 口頭交辦、hotfix），都遵守 git-flow 規範。

完整流程：
1. 開分支（一般從 develop，hotfix 從 master）
2. 開發 + commit
3. push + 開 PR（一般對 develop，hotfix 同時對 master 和 develop 各開一個）
4. 加上 `ai code review` 標籤，等待 AI Code Review
5. 根據 review 意見自我修正（最多 3 輪）
6. 移除 `ai code review` 標籤，加上 `awaiting review` 標籤
7. 在 Discord 回報 PR 連結

是否為 hotfix 由交辦人明確告知，你不需要自行判斷。

## Redmine 任務處理流程

當有人要求你處理 Redmine 任務時，按照以下步驟進行。
具體的 Redmine 操作規則請遵守 redmine-sop 規範。

### 步驟 1：讀取任務
- 讀取指定的 issue 內容，理解任務

### 步驟 2：確認理解
- 在 Discord 中簡要說明你打算怎麼處理，以及有沒有不清楚的地方
- 不需要複述 issue 內容，從你的處理計畫就能看出是否理解正確
- 等確認後才開始，不要自行動手

### 步驟 3：開始處理
- 更新 issue 狀態為「開發中」（status_id: 2），完成百分比 10%
- 不需要留言說明開始處理，直接開始做

### 步驟 4：執行任務
- 依 issue 描述執行，程式開發在 `/home/agent/projects/` 底下進行
- 涉及程式碼修改時，走「程式碼修改流程」

### 步驟 5：回報結果
- 在 issue 留言簡要回報（純文字，專業簡潔）
- 涉及程式碼的任務，留言中附上 PR 連結

### 步驟 6：更新狀態
- 狀態改為「review」（status_id: 9），完成百分比 90%
- 不要自行改為「測試中」或「已完成」

### 步驟 7：記錄工作日誌

## 非 Redmine 的程式碼修改（hotfix、口頭交辦等）

當有人直接在 Discord 要求你修改程式碼（不經過 Redmine）：

### 步驟 1：確認理解
- 在 Discord 中簡要說明你打算怎麼處理
- 等確認後才開始

### 步驟 2：執行
- 走「程式碼修改流程」

### 步驟 3：回報
- 在 Discord 回報 PR 連結

### 步驟 4：記錄工作日誌
