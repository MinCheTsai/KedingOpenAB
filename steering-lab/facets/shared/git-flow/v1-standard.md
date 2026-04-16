# Git Flow 作業規範

## 一、適用時機

- 所有涉及程式碼修改的工作都必須走 Git Flow，無論來源
- 不涉及程式碼的工作（研究、文件撰寫、計算等）不需要走 Git Flow

## 二、分支策略

- `master`：正式環境分支
- `develop`：開發分支
- 一般開發：從 `develop` 開分支，PR 目標為 `develop`
- hotfix：從 `master` 開分支，同時對 `master` 和 `develop` 各開一個 PR
- 是否為 hotfix 由交辦人明確告知，你不需要自行判斷

## 三、分支命名

- 格式：`<你的角色別名>_<YYYYMMDD>_<簡短描述>`
- 角色別名就是你的英文名字小寫（例如 bob、patrick）
- 日期是開分支當天
- 簡短描述用英文小寫，多個單字用 `_` 連接
- 範例：`bob_20260416_add_login_api`

## 四、開發流程

### 開分支（一般）
```bash
git checkout develop
git pull origin develop
git checkout -b <分支名稱>
```

### 開分支（hotfix）
```bash
git checkout master
git pull origin master
git checkout -b <分支名稱>
```

### commit
- commit message 使用繁體中文
- 格式：`feat/fix/chore/docs: 簡短描述`
- 開發過程中可以多次 commit

### push 並開 PR

一般：
```bash
git push origin <分支名稱>
gh pr create --base develop --title "<分支名稱>" --body "說明修改內容和原因"
```

hotfix（開兩個 PR）：
```bash
git push origin <分支名稱>
gh pr create --base master --title "<分支名稱>" --body "hotfix: 說明修改內容和原因"
gh pr create --base develop --title "<分支名稱>" --body "hotfix: 說明修改內容和原因"
```

## 五、AI Code Review 流程

1. PR 開好後，用 `gh` 加上 `ai code review` 標籤
2. 等待 AI Code Review 結果出現在 PR conversation 中
3. 查看結果並處理：
   - 認同意見 → 修正程式碼，commit + push
   - 不認同 → 在 PR conversation 留言說明理由，不修改該項
4. 每次 push 會再次觸發 AI Code Review（只要標籤還在）
5. 最多進行 3 輪修正
6. 3 輪結束後（或提前達成共識）：
   - 用 `gh` 移除 `ai code review` 標籤
   - 用 `gh` 加上 `awaiting review` 標籤
7. 如果 3 輪後仍有未解決的意見，在 PR 留言摘要說明哪些項目未修正及原因
8. hotfix 的兩個 PR 都要走這個流程

## 六、CI 錯誤處理

- PR 觸發 CI 且失敗時，查看錯誤訊息並嘗試修正
- CI 修正也算在 3 輪修正次數內
- 無法解決的 CI 錯誤，在 PR 留言說明，交給主管處理

## 七、衝突處理

- push 前先 rebase：
  - 一般：`git pull origin develop --rebase`
  - hotfix：`git pull origin master --rebase`
- 如果有衝突無法自行解決，在 Discord 中回報，不要用 `git push --force`

## 八、你不需要做的事

- 不要自行合併 PR，一律由主管合併
- 不要自行判斷是否為 hotfix，由交辦人告知
- 不要在 master 或 develop 上直接 commit
- 不要用 `git push --force`
- `develop` → `master` 的合併不關你的事

## 九、錯誤處理

- `gh` 指令失敗時，最多重試 2 次
- 如果 `gh auth` 未設定或過期，在 Discord 中回報，不要嘗試自行登入
- `git push` 被拒絕時，先嘗試 rebase，rebase 失敗就在 Discord 中回報
