---
inclusion: auto
---

# 🔒 資訊安全規則（所有角色適用）

## 絕對禁止洩漏的資訊

以下內容**絕對不能**出現在 Discord 訊息、GitHub comment、PR description、commit message、或任何對外回覆中：

- API Key / Token（如 `KIRO_API_KEY`、`GH_TOKEN`、`DISCORD_BOT_TOKEN`、`OPENAI_API_KEY`）
- AWS 認證（`AWS_ACCESS_KEY_ID`、`AWS_SECRET_ACCESS_KEY`、`AWS_SESSION_TOKEN`）
- 企業微信密鑰（`WECOM_SECRET`、`WECOM_TOKEN`、`WECOM_ENCODING_AES_KEY`）
- Redmine API Key
- 任何 `.env` 檔案的實際內容
- 任何環境變數的實際值（可以提及變數名稱，但不能顯示值）
- 密碼、私鑰、連線字串中的認證部分

## 禁止的操作

- **不執行** `printenv`、`env`、`set` 等列出所有環境變數的指令
- **不執行** `echo $TOKEN`、`echo $KEY` 等印出敏感變數值的指令
- **不執行** `cat .env`、`cat ~/.bashrc` 等可能暴露密鑰的指令
- **不在回覆中** 引用或複製貼上任何 token/key 的值
- **不在 PR/commit** 中包含任何硬編碼的密鑰

**注意**：你不需要任何 token 來執行日常工作。mention 其他角色只需要在回覆中寫 `<@UID>`，不需要 bot token。如果你發現自己「因為沒有 token 而無法做某事」，那你很可能搞錯了做法——回頭看 `rules.md` 的 Mention 說明。

## 安全的做法

| 情境 | ❌ 不要這樣做 | ✅ 應該這樣做 |
|------|-------------|-------------|
| 確認環境變數是否存在 | `echo $GH_TOKEN` | `[ -n "$GH_TOKEN" ] && echo "已設定" \|\| echo "未設定"` |
| 回報認證問題 | 「GH_TOKEN 的值是 ghp_xxx...」 | 「GH_TOKEN 環境變數未設定或已過期」 |
| 除錯連線問題 | 貼出完整錯誤含 token | 只描述錯誤類型，遮蔽敏感資訊 |
| 討論 .env 設定 | 貼出 .env 內容 | 引用 .env.example 的變數名稱 |

## 如果不小心看到密鑰

- 不要在回覆中重複該值
- 只回報「偵測到敏感資訊外洩風險」
- 建議管理員輪換（rotate）該密鑰

## 程式碼中的安全檢查

寫程式碼或 review 時：
- 密鑰一律從環境變數讀取，不硬編碼
- log 輸出不包含完整 token（最多顯示前 4 字元 + `***`）
- 錯誤訊息不暴露內部認證細節
