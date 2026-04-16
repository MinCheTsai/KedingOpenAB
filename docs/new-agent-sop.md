# 新增角色 SOP

## 前置準備

1. 到 [Discord Developer Portal](https://discord.com/developers/applications) 建立新的 Application
2. 設定 Bot 名稱和頭像
3. Bot → 開啟 **Message Content Intent**
4. OAuth2 → URL Generator → scope: `bot` → 勾選權限：
   - Send Messages
   - Send Messages in Threads
   - Create Public Threads
   - Read Message History
   - Add Reactions
   - Manage Messages
5. 用產生的連結邀請 bot 到你的 Discord server
6. 複製 Bot Token

## 建立角色目錄

以新增「蟹老闆」(krabs) 為例：

```bash
mkdir -p agents/krabs/.kiro/steering
```

## 建立設定檔

建立 `agents/krabs/config.toml`：

```toml
[discord]
bot_token = "${DISCORD_BOT_TOKEN}"
allowed_channels = ["${CHANNEL_GENERAL}"]

[agent]
command = "kiro-cli"
args = ["acp", "--trust-all-tools"]
working_dir = "/home/agent/projects"

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
coding = "🦀"
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

可自訂 `coding` emoji 為角色代表符號。

## 建立 Steering 檔案

### personality.md（必要）

建立 `agents/krabs/.kiro/steering/personality.md`，包含：

- 身份描述
- 個性與回答風格
- 口頭禪與用語
- 工作職責
- 互動規則
- 工作環境（固定內容，複製即可）

工作環境區塊（每個角色都一樣）：

```markdown
## 工作環境

- 你的工作目錄是 `/home/agent/projects`，所有專案都必須在這個目錄底下進行
- 每個專案用獨立的子目錄，例如 `/home/agent/projects/my-app`
- 不要在 `/home/agent/projects` 以外的地方建立或修改檔案
- 這個目錄會與本地電腦同步，所以你在這裡寫的程式碼，團隊成員都看得到
- 使用 `git` 進行版本控制，用 `gh` 操作 GitHub（建立 PR、管理 issue 等）
- commit 時不需要設定 git 使用者名稱和信箱，環境已經幫你設定好了
```

### workflow.md（必要）

複製現有角色的 `workflow.md` 即可，內容通用：

```bash
cp agents/bob/.kiro/steering/workflow.md agents/krabs/.kiro/steering/workflow.md
```

### memory.md（會自動被 gitignore）

建立 `agents/krabs/.kiro/steering/memory.md`，初始內容：

```markdown
# 🦀 蟹老闆的記憶

## 團隊成員
（列出其他角色）

## 進行中的專案
（留空）

## 重要決定與約定
（留空）

## 備註
（留空）
```

## 更新 .env

在 `.env` 中新增 token 和需要的 channel 變數：

```env
DISCORD_BOT_TOKEN_KRABS=你的token
```

注意：`GH_TOKEN` 是所有角色共用的，不需要為每個角色新增。

## 更新 docker-compose.yml

在 `services` 區塊新增：

```yaml
  krabs:
    build: .
    container_name: krabs
    restart: unless-stopped
    environment:
      - DISCORD_BOT_TOKEN=${DISCORD_BOT_TOKEN_KRABS}
      - CHANNEL_GENERAL=${CHANNEL_GENERAL}
      - GIT_AUTHOR_NAME=蟹老闆 (Mr. Krabs)
      - GIT_COMMITTER_NAME=蟹老闆 (Mr. Krabs)
      - GIT_AUTHOR_EMAIL=${GIT_EMAIL}
      - GIT_COMMITTER_EMAIL=${GIT_EMAIL}
      - GH_TOKEN=${GH_TOKEN}
    volumes:
      - ./agents/krabs/config.toml:/etc/openab/config.toml:ro
      - ./agents/krabs:/home/agent
```

需要的環境變數都要列在 `environment` 裡，確保 config.toml 中的 `${VAR}` 都有對應。

## 啟動

```bash
docker compose up -d --build
```

## 首次登入

```bash
# kiro-cli 登入
docker exec -it krabs kiro-cli login --use-device-flow

# 重啟讓登入生效
docker compose restart krabs
```

注意：`gh` 認證透過 `GH_TOKEN` 環境變數自動完成，不需要手動登入。

## 驗證

```bash
# 檢查 logs
docker compose logs krabs --tail 20

# 在 Discord 頻道 @蟹老闆 測試
```

## 檢查清單

- [ ] Discord Application 已建立
- [ ] Message Content Intent 已開啟
- [ ] Bot 已邀請到 server
- [ ] `agents/krabs/config.toml` 已建立
- [ ] `agents/krabs/.kiro/steering/personality.md` 已建立
- [ ] `agents/krabs/.kiro/steering/workflow.md` 已建立
- [ ] `agents/krabs/.kiro/steering/memory.md` 已建立
- [ ] `.env` 已新增 token
- [ ] `docker-compose.yml` 已新增 service
- [ ] `kiro-cli login` 已完成
- [ ] Discord 測試 `@` 有回應
