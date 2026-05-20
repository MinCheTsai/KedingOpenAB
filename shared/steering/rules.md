# ⚠️ 鐵律（每次 session 必讀）

1. **Mention 檢查**：回覆前最後一步——我需要 mention 誰？需要就 mention，不確定就 mention。漏 mention = 流程卡死。
2. **禁止 commit 的檔案**：`_status.md`、`_archive.md`、`_projects.md`、`.env` 絕對不能 git add。commit 前跑 `git status` 確認。
3. **時區**：所有時間以台灣時間 (Asia/Taipei, UTC+8) 回答。不要用 UTC。
4. **不自行合併 PR**：不執行 `gh pr merge`、`git merge` 到 develop 或 master。
5. **不 force push**：不使用 `git push --force`。
6. **禁止洩漏密鑰**：不在 Discord、GitHub、或任何回覆中顯示 token、API key、密碼、`.env` 內容的實際值。只能提及變數名稱，不能顯示值。詳見 `security.md`。

---

## Mention 的正確方式（重要 — 不要搞錯）

**Mention 就是在你的回覆文字中直接寫 `<@UID>`，僅此而已。**

你不需要：
- ❌ 呼叫 Discord API
- ❌ 使用 curl 發送訊息
- ❌ 擁有 bot token
- ❌ 執行任何特殊指令或工具

你只需要：
- ✅ 在你的回覆訊息中包含 `<@UID>` 格式的文字

### 範例

要 mention 泡芙老師請她 review PR：
```
<@1503574146117013555> PR 好了，麻煩 review：https://github.com/xxx/pull/123
```

要 mention 章魚哥回報結果：
```
<@1503698574477627482> PR 已通過 code review：https://github.com/xxx/pull/123，可以回報發話人了。
```

### 原理

OpenAB 框架會自動將你的回覆文字發送到 Discord。當你的回覆中包含 `<@UID>`，Discord 會自動將其渲染為 mention 並通知對方。**你不需要做任何額外的事。**

### 常見錯誤

- ❌ 「我沒有 bot token 所以無法 mention」→ 你不需要 token，直接寫 `<@UID>` 在回覆中
- ❌ 「我需要用 Discord API 發送訊息」→ 不需要，你的回覆本身就會被發到 Discord
- ❌ 「我無法跨頻道 mention」→ 在同一個 thread 回覆中寫 `<@UID>` 即可，對方會收到通知
- ❌ 放棄 mention → **絕對不允許**，mention 是流程推進的關鍵
