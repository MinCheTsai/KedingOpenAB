# OpenAB 版本更新 SOP

## 原則

- 使用**指定版本**的 image，不用 `latest` tag
- 無論是否為 beta，都以最新 release 版本更新
- 更新前查閱 release notes 確認有無 breaking changes

## 查閱最新版本

1. 到 [OpenAB Releases](https://github.com/openabdev/openab/releases) 查看最新版本
2. 或查看本地 clone：`git -C refs/openab fetch --tags && git -C refs/openab tag --sort=-v:refname | head -5`

## 更新步驟

```bash
# 1. 修改 Dockerfile 的 FROM tag
#    例：FROM ghcr.io/openabdev/openab:0.8.3-beta.5
vi Dockerfile

# 2. 更新本地 OpenAB 原始碼參考
git -C refs/openab pull

# 3. Build 並重啟
docker compose build --pull
docker compose up -d --force-recreate bob patrick puff squidward sandy

# 4. 確認啟動正常
docker logs bob --tail 10
```

## 確認清單

- [ ] `docker logs <agent>` 有正常啟動（`discord bot connected`）
- [ ] 新功能的 config 參數有出現在啟動 log 中
- [ ] Discord 上測試基本互動正常

## 版本紀錄

| 日期 | 版本 | 備註 |
|------|------|------|
| 2026-05-19 | 0.8.3-beta.5 | 加入 allowed_role_ids 支援 |

## 注意事項

- OpenAB 的 `latest` tag 只在 stable release 時更新，beta 版不會推到 `latest`
- CI/CD 設定在 `.github/workflows/build.yml`，promote-stable 才會推 `latest`
- 原始碼參考放在 `refs/openab/`（已在 .gitignore 排除）
