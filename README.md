# AI 课程题库练习

这是一个完全离线的练习网页，题目来自同目录中的 7 份 PDF。

## 使用

直接双击 `index.html`，用浏览器打开即可。

- **顺序练习**：严格按 PDF 文件名和 PDF 内题目顺序练习。
- **错题练习**：只显示错题本中的题目；在错题模式答对后会自动移出错题本。
- **模拟测试（`/practice`）**：自定义考试范围（按 PDF 勾选）与各题型数量随机组卷；答题卡可跳题、随时交卷。交卷后自动判分并给出逐题解析，错题按题目 ID **去重**后加入错题集（同一题重复答错只累加次数，不会重复）。填空 / 计算题按忽略空格标点的规则判分，若判分有误可在解析页「我答对了 / 算我答错」手动改判。
- **选择 / 判断题**：选项作答后自动判分，答错自动加入错题本。
- **填空 / 简答 / 计算题**：无需输入答案，点击「显示答案」后用「正确 / 错误」自评；默认正确，可用上下键切换，按回车进入下一题；选择错误会加入错题本。
- **上一题 / 下一题**：可随时返回上一题复看；本轮已作答的题目会保留作答状态，不会重复计分（也可用键盘 ← / → 翻题）。
- **手动修正**：提交后可以手动加入或移出错题本；错题练习中也可用“不再练这题”直接删除。
- **已学进度**：首页「题库概览」显示总进度及每份 PDF 的已学题数（作答或查看答案后即计入）。
- **深色模式**：右上角按钮切换浅色 / 深色主题，偏好保存在浏览器中；默认跟随系统设置。
- **自动保存**：练习进度、答题次数和错题记录保存在当前浏览器的 `localStorage` 中。
- **查看原题**：练习页可打开对应 PDF 页进行核对。

如果更换浏览器、使用隐私模式或清除浏览器站点数据，记录会丢失。

## 本地服务

运行：

```powershell
.\start-local.ps1
```

然后访问 `http://127.0.0.1:8788`。服务使用并发 HTTP 处理器，可同时为多个用户提供静态页面，并支持 `/practice` 路由。每个用户的进度仍单独保存在自己的浏览器中，不会互相看到，也不会跨设备同步。

## Cloudflare Pages 部署

主部署方式改为：先把代码推送到 GitHub，再在 Cloudflare Pages 控制台手动连接该 GitHub 仓库。之后每次推送到生产分支，Cloudflare 会自动拉取仓库、运行构建命令并发布。部署产物只包含网页、脚本、样式和 PDF，不会把本地服务脚本、Tunnel 配置或开发目录发布出去。

一次性准备：

1. 在 GitHub 创建仓库，并把本项目推送上去。
2. 打开 Cloudflare 控制台，进入 `Workers & Pages`，创建 Pages 项目。
3. 选择 `Connect to Git`，授权 GitHub，然后选择这个仓库。
4. 构建设置填写：
   - Framework preset: `None`
   - Production branch: `main`
   - Build command: `npm run build`
   - Build output directory: `dist`
   - Root directory: 留空（仓库根目录）
5. 保存并部署。以后推送到 `main` 分支会自动触发 Cloudflare Pages 重新构建和发布。

本地验证构建：

```powershell
npm run build
```

构建产物会生成到 `dist/`。Cloudflare Pages 使用 `_redirects` 将 `/practice` 重写到 `practice.html`，并使用 `_headers` 设置基础安全头和缓存策略。

如果 Cloudflare 报错 `Asset too large`，并且路径里出现 `node_modules/workerd/bin/workerd`，说明 Cloudflare 正在上传仓库根目录而不是 `dist/`。回到 Pages 项目的 `Settings -> Build & deployments`，确认：

- Build command: `npm run build`
- Build output directory: `dist`
- Root directory: 留空

仓库中的 `wrangler.jsonc` 同时固定了 Pages 的 `pages_build_output_dir` 和 Workers 静态资源的 `assets.directory` 为 `./dist`。如果当前 Cloudflare 流程执行的是 `wrangler deploy`，`src/worker.js` 会作为 Worker 入口，并把 `/practice` 转到 `practice.html`；`.assetsignore` 用于防止静态资产上传流程误传 `node_modules` 等本地文件。

旧的 `start-public.ps1` / `cloudflared-aitest.yml` 只保留作临时 Tunnel 发布备用，不再是推荐部署方式。

## Public 仓库与 main 分支规则

本仓库如果设为 public，建议把 `main` 当作生产分支保护起来。先推送一次 `.github/workflows/ci.yml`，等 GitHub Actions 跑出检查项后，在 GitHub 仓库的 `Settings -> Rules -> Rulesets`（或 `Branches -> Branch protection rules`）中为 `main` 增加规则：

- Restrict target branches: `main`
- Require a pull request before merging: 开启。多人协作时要求至少 1 个 approval；单人维护时也建议通过 PR 合并，便于触发预览和检查。
- Require status checks to pass: 开启，并选择 `Build and validate static site`。
- Require branches to be up to date before merging: 开启，避免旧分支绕过最新检查。
- Require conversation resolution before merging: 开启。
- Block force pushes: 开启。
- Restrict deletions: 开启。
- Require linear history: 建议开启，让生产分支历史更容易回滚和审计。
- Require signed commits: 可选；如果你的本机 Git 已配置签名再开启，否则会影响日常提交。

仓库安全设置建议：

- 开启 Secret scanning 和 Push protection，防止 Cloudflare token、Tunnel 凭据、`.env` 等密钥进入 public 仓库。
- GitHub Actions 的默认权限设为只读；当前 CI 已显式使用 `permissions: contents: read`。
- 不提交 `dist/`、`node_modules/`、`.wrangler/`、`.dev.vars`、`.env`、Cloudflare Tunnel 凭据；这些已由 `.gitignore` / `.assetsignore` 覆盖。
- Cloudflare Pages 的生产分支只设为 `main`，构建命令保持 `npm run build`，输出目录保持 `dist`。

不要把 Cloudflare 部署成功本身设为合并前必需检查，除非你已经配置了 PR preview deployment。否则生产部署通常发生在合并到 `main` 之后，可能造成规则互相等待。
## 重新生成题库

当 PDF 内容发生变化时，在本目录运行：

```powershell
python .\scripts\build_questions.py
```

脚本依赖 `pypdf`，生成的 `questions.js` 可供离线网页直接读取。




