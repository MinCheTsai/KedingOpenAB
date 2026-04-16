# MCP 連線設定參考

> 記錄各 MCP server 的連線設定，供角色 `mcp.json` 配置時參考。

## 設定檔位置

- 角色層級：`agents/<角色>/.kiro/settings/mcp.json`
- Kiro IDE 層級：`.kiro/settings/mcp.json`

---

## Redmine MCP

- 套件：[redmine-mcp-server](https://pypi.org/project/redmine-mcp-server/)
- 傳輸方式：HTTP Streamable（endpoint: `/mcp`）
- 認證：透過 server 端環境變數 `REDMINE_API_KEY`，client 端不需帶 token
- 部署指南：`docs/mcp-redmine-deploy.md`

```json
{
  "redmine": {
    "url": "http://<mcp-server-ip>:<port>/mcp",
    "autoApprove": [
      "get_redmine_issue",
      "list_redmine_issues",
      "search_redmine_issues",
      "create_redmine_issue",
      "update_redmine_issue",
      "list_redmine_projects",
      "list_project_members",
      "search_entire_redmine"
    ]
  }
}
```

> 歷史備註：最初使用 runekaagaard/mcp-redmine（SSE transport），
> 因 MCP Python SDK 的 DNS rebinding protection 導致 Docker 容器間連線回 421，
> 於 2026-04-16 改用 jztan/redmine-mcp-server（HTTP Streamable），問題解決。

---

## HRS MCP（科定報價系統）

- 傳輸方式：HTTP Streamable
- 認證：Bearer Auth

```json
{
  "hrs": {
    "url": "http://<host>:<port>/mcp/pricing",
    "headers": {
      "Authorization": "Bearer <token>"
    },
    "autoApprove": [
      "GetRoomDoorPrice",
      "GetRoomDoorFramePrice",
      "GetRoomDoorAccessories",
      "GetCabinetDoorPrice",
      "GetCabinetShippingFee",
      "GetFlooringPrice",
      "GetFlooringAccessories"
    ]
  }
}
```

---

## 設定要點

1. `autoApprove`：kiro-cli ACP 模式下必須設定，否則工具呼叫會等待人工確認（Discord 上無法確認）
2. `headers`：需要認證的 MCP server 在此帶 Bearer token
3. `url`：MCP server 部署在遠端主機時，使用內網 IP 連線
