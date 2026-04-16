---
inclusion: manual
---

# Steering Lab 操作原則

本專案使用 `steering-lab/` 管理 AI 角色的行為實驗。

## 核心規則

1. **不直接改 steering**：不要直接修改 `agents/<角色>/.kiro/steering/` 裡的檔案，所有變更都透過 steering-lab 的 facets + profiles 管理
2. **先讀現況**：討論 steering 相關話題前，先讀 `steering-lab/experiments.md` 和對應角色的 profile
3. **版本化**：新的 steering 變更建立新檔案（`exp-` 或 `v<N>-`），不覆蓋現有版本
4. **記錄實驗**：每次變更都在 `experiments.md` 留下紀錄

## 快速參考

- 模板庫：`steering-lab/facets/`
- 組合定義：`steering-lab/profiles/<角色>/`
- 實驗紀錄：`steering-lab/experiments.md`
- 套用腳本：`./steering-lab/apply.sh <角色> <組合>`
- 操作指引：`steering-lab/README.md`
