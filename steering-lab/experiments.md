# 🧪 實驗紀錄

> 每次 steering 實驗都記錄在這裡，方便回溯和對齊。
> 格式：實驗編號、角色、組合、目的、結果、結論。

---

## EXP-001 — 海綿寶寶 Redmine 自動任務處理

- **日期**：2026-04-16
- **角色**：bob
- **組合**：`exp-redmine`
- **面向變更**：
  - `workflow`: v1-worklog → exp-redmine-auto（新增 Redmine 自動讀取 + 處理 + 回報流程）
  - `mcp-tools`: v1-redmine → v2-redmine（改用 redmine-mcp-server 的專用工具）
  - `personality`: v1-base（不變）
- **目的**：驗證海綿寶寶能否透過 MCP 自動讀取 Redmine issue、執行任務、回覆留言、更新狀態
- **測試方式**：在 Discord 跟海綿寶寶說「去看你的 Redmine 任務」
- **結果**：✅ 基本流程跑通，海綿寶寶成功讀取 issue #1221 並回覆留言
- **待改善**：
  - 接收到 issue 編號後的處理順序仍需調教（步驟執行順序、留言格式等）
  - Redmine 工作流程（狀態轉換規則）尚未明訂，需請開發主管提供團隊 SOP
  - 需要觀察更多實際對話紀錄來迭代 workflow steering
- **下一步**：收集海綿寶寶的 Discord 對話紀錄，逐步調整 exp-redmine-auto.md
