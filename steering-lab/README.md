# 🧪 Steering Lab — 角色行為實驗室

## 這是什麼

Steering Lab 是比奇堡開發團隊的角色行為實驗框架。
每個 AI agent 的行為由 steering 檔案定義，這裡管理所有 steering 的版本、組合、實驗紀錄。

## 核心概念

### 實驗 vs 正式版本

- **實驗版本**（`exp-`）：正在測試的 steering，隨時可能調整或廢棄
- **正式版本**（`v1`, `v2`...）：經過驗證、確認有效的 steering，會長期使用
- 一個實驗版本經過驗證後，可以「畢業」成為正式版本

### Steering 分類

每個角色的 steering 拆成獨立的面向（facet），各自版本化：

| 面向 | 說明 | 範例 |
|------|------|------|
| `personality` | 角色個性、口頭禪、互動風格 | 海綿寶寶的熱情個性 |
| `workflow` | 工作流程、任務處理方式 | 被動等指令 vs 主動讀 Redmine |
| `mcp-tools` | MCP 工具說明與使用指引 | Redmine API 操作方式 |
| `collaboration` | 跨角色協作規則 | 誰負責什麼、怎麼分工（未來） |

### 組合（Profile）

一個「組合」是一組 steering 面向的特定版本搭配，定義在 `profiles/` 底下。
切換組合 = 切換角色的完整行為模式。

## 目錄結構

```
steering-lab/
├── README.md                 ← 你正在看的這份文件
├── experiments.md            ← 實驗紀錄（所有角色共用）
├── apply.sh                  ← 套用組合的腳本
├── profiles/                 ← 組合定義
│   └── bob/
│       ├── default.txt       ← 目前使用的組合
│       └── exp-redmine.txt   ← 實驗組合
├── facets/                   ← Steering 模板庫
│   ├── shared/               ← 跨角色共用
│   │   └── mcp-tools/
│   ├── bob/
│   │   ├── personality/
│   │   └── workflow/
│   └── patrick/
│       ├── personality/
│       └── workflow/
└── archive/                  ← 廢棄的實驗版本（留存參考）
```

## 操作方式

### 1. 查看角色目前使用的組合

```bash
cat steering-lab/profiles/bob/default.txt
```

### 2. 套用組合到角色

```bash
# 套用 bob 的 default 組合
./steering-lab/apply.sh bob default

# 套用 bob 的實驗組合
./steering-lab/apply.sh bob exp-redmine
```

### 3. 新增實驗

1. 在 `facets/<角色>/` 底下建立新版本的 steering 檔案（命名 `exp-xxx.md`）
2. 在 `profiles/<角色>/` 建立新的組合檔（`.txt`）
3. 在 `experiments.md` 記錄實驗目的
4. 用 `apply.sh` 套用
5. 重啟角色容器測試
6. 在 `experiments.md` 記錄結果

### 4. 實驗畢業為正式版本

1. 確認實驗結果符合預期
2. 將 `exp-xxx.md` 重新命名為 `v<N>-xxx.md`
3. 更新 `profiles/<角色>/default.txt` 指向新版本
4. 在 `experiments.md` 標記畢業
5. 套用並提交 git

### 5. 廢棄實驗

1. 在 `experiments.md` 標記廢棄原因
2. 將檔案移到 `archive/`（或直接刪除，git 裡還有紀錄）

## 與 Kiro IDE 的協作約定

每次討論 steering 相關話題時：
1. 先讀 `steering-lab/experiments.md` 了解目前實驗狀態
2. 先讀 `steering-lab/profiles/<角色>/default.txt` 了解目前使用的組合
3. 修改 steering 時，在 facets 裡建新版本，不要直接改現有版本
4. 每次變更都記錄在 `experiments.md`

## 未來展望

- **多角色協作**：蟹老闆分配 Redmine issue → 海綿寶寶做前端 → 派大星做後端
- **collaboration facet**：定義角色間的溝通協議和分工規則
- **自動化測試**：定義 steering 的驗收標準，自動跑測試場景
