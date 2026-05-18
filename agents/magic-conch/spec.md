# 🐚 神奇海螺 (Magic Conch) — 角色規格

## 概要

| 項目 | 內容 |
|------|------|
| 角色名稱 | 🐚 神奇海螺 (Magic Conch / conch) |
| 類型 | Discord Bot（非 AI agent，輕量腳本型） |
| 核心職責 | 容器健康監控、生命管理（重啟/停止/診斷） |
| 互動方式 | Slash Command |
| 權限需求 | 存取 Docker API（透過 docker.sock） |

## 背景

目前團隊的 bot 以 Docker 容器運行，偶爾會莫名掛掉（根因尚未查明）。需要一個角色能快速查看狀態、重啟容器，降低人工介入成本。

## 設計原則

- **輕量優先**：不跑 LLM，純腳本 + Docker API
- **參考小蝸模式**：以 slash command 為主要互動方式
- **最小權限**：未來可透過 docker-socket-proxy 只開放必要的 Docker API
- **自身高可用**：設定 `restart: always`，確保海螺自己不會掛掉沒人救

## 角色名稱對應

| 暱稱 | 容器名稱 |
|------|---------|
| 海綿寶寶 / bob | bob |
| 派大星 / patrick | patrick |
| 章魚哥 / squidward | squidward |
| 珊迪 / sandy | sandy |
| 泡芙老師 / puff | puff |
| 小蝸 / gary | slash-bot |
| 企微 / wecom | wecom-bot |
| gateway | gateway |

## 權限控制

| 指令類型 | 允許使用者 |
|---------|-----------|
| status / diagnose / logs / rollcall | 所有人 |
| heal / watch | 管理員 + 操作員 role |
| kill / restart-all | 僅管理員 |

## 回應風格

簡短、神秘、果斷：

- status 正常 → 「🐚 海綿寶寶...活著。」
- status 掛了 → 「🐚 海綿寶寶...沉默了。」
- heal 成功 → 「🐚 ...已重啟。」
- kill → 「🐚 ...如你所願。」
- rollcall → 「🐚 全員...回報。」+ 列表

## 技術架構

```
┌─────────────────┐
│  神奇海螺 Bot    │  (輕量容器, restart: always)
│  - discord.py   │
│  - docker SDK   │
└────────┬────────┘
         │ (docker.sock)
┌────────▼────────┐
│ Docker Daemon   │
└─────────────────┘
```

## 來源

- 發起人：米哥
- 討論場景：🗿 會議室
- 日期：2026-05-17
- 規格整理：珊迪
