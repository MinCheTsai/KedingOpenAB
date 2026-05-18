# Thread 封存機制設計

## 問題

Discord thread 超過 ~300 則訊息後，OpenAB 的 `multibot-mentions` participant tracking 會錯亂，導致所有 bot 搶答。

## 解決方案：自動封存 + 開新 thread

當 thread 訊息數達到閾值時，自動：
1. 總結當前對話
2. 在同一個頻道開新 thread
3. 在新 thread mention 所有參與過的 bot，附上總結
4. 舊 thread 標記為已封存（發一則結尾訊息指向新 thread）

## 觸發條件

- Thread 訊息數 ≥ 200（保守值，避免到 300 才出問題）
- 觸發時機：每次 bot 回覆後檢查（或用 cron 定期掃描）

## 實作方式

### 方案 A：Bot 自主檢查（推薦）

每個 bot 回覆後，檢查當前 thread 訊息數。如果超過閾值：

```bash
# 1. 取得 thread 訊息數
MSG_COUNT=$(curl -s "https://discord.com/api/v10/channels/${THREAD_ID}" \
  -H "Authorization: Bot ${DISCORD_BOT_TOKEN}" | jq '.message_count')

# 2. 如果超過閾值，觸發封存
if [ "$MSG_COUNT" -ge 200 ]; then
  # 執行封存流程
fi
```

### 方案 B：獨立服務（magic-conch 擴充或新服務）

新增一個定期掃描服務，檢查所有活躍 thread 的訊息數，超過閾值就觸發封存。

## 封存流程細節

### Step 1: 總結對話

用 `/export-thread` 匯出 thread 內容，然後請 LLM 產生摘要：
- 討論了什麼
- 目前進度
- 待辦事項
- 參與的 bot 和人類

### Step 2: 在舊 thread 發結尾訊息

```
📦 此對話已封存（訊息數達上限）。
討論延續至新 thread：[新 thread 連結]
```

### Step 3: 在同頻道開新 thread

用 Discord API 發一則新訊息並開 thread：

```bash
# 發訊息到原頻道
MSG=$(curl -s -X POST "https://discord.com/api/v10/channels/${CHANNEL_ID}/messages" \
  -H "Authorization: Bot ${DISCORD_BOT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"content\": \"🔄 延續討論（封存自舊 thread）\n\n@bot1 @bot2\n\n**前情提要：**\n${SUMMARY}\"}")

# 開 thread
MSG_ID=$(echo "$MSG" | jq -r '.id')
curl -s -X POST "https://discord.com/api/v10/channels/${CHANNEL_ID}/messages/${MSG_ID}/threads" \
  -H "Authorization: Bot ${DISCORD_BOT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"${THREAD_TITLE}（續）\"}"
```

### Step 4: Mention 所有參與者

在新 thread 的第一則訊息 mention 所有原 thread 參與過的 bot，讓他們建立 session。

## 需要的權限

- Bot 需要 `MANAGE_THREADS` 權限（開新 thread）
- Bot 需要 `SEND_MESSAGES` 權限（在頻道發訊息）
- Bot 需要 `READ_MESSAGE_HISTORY` 權限（讀取 thread 訊息數）

## 設定（config.toml 新增）

```toml
[thread_archive]
enabled = true
max_messages = 200          # 觸發封存的訊息數閾值
summary_model = "auto"      # 用哪個模型產生摘要
archive_message = true      # 是否在舊 thread 發結尾訊息
```

## 替代方案：向 OpenAB 提 Feature Request

這個功能如果能內建在 OpenAB 會更好（Rust 層面直接處理，不需要每個 bot 自己檢查）。可以到 GitHub 開 issue 建議。

## 狀態

- [ ] 決定用方案 A 還是方案 B
- [ ] 實作
- [ ] 測試
