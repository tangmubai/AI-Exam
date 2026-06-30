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

## GitHub + Cloudflare Pages 部署

主部署方式改为：代码推送到 GitHub 后，由 GitHub Actions 构建静态文件并发布到 Cloudflare Pages。部署产物只包含网页、脚本、样式和 PDF，不会把本地服务脚本、Tunnel 配置或开发目录发布出去。

一次性准备：

1. 在 Cloudflare Pages 创建项目，默认项目名使用 `ai-exam`。如果你使用其他项目名，在 GitHub 仓库变量中设置 `CLOUDFLARE_PAGES_PROJECT_NAME`。
2. 在 Cloudflare 创建 API Token，权限至少包含对应账号的 Cloudflare Pages 编辑权限。
3. 在 GitHub 仓库的 `Settings -> Secrets and variables -> Actions` 中添加：
   - Secret: `CLOUDFLARE_ACCOUNT_ID`
   - Secret: `CLOUDFLARE_API_TOKEN`
   - Variable（可选）: `CLOUDFLARE_PAGES_PROJECT_NAME`
4. 推送到 `main` 分支后，`.github/workflows/deploy-cloudflare-pages.yml` 会自动运行部署。

本地验证构建：

```powershell
npm run build
```

构建产物会生成到 `dist/`。Cloudflare Pages 使用 `_redirects` 将 `/practice` 重写到 `practice.html`，并使用 `_headers` 设置基础安全头和缓存策略。

如需手动部署：

```powershell
npm run build
npx wrangler@latest pages deploy dist --project-name ai-exam
```

旧的 `start-public.ps1` / `cloudflared-aitest.yml` 只保留作临时 Tunnel 发布备用，不再是推荐部署方式。

## 重新生成题库

当 PDF 内容发生变化时，在本目录运行：

```powershell
python .\scripts\build_questions.py
```

脚本依赖 `pypdf`，生成的 `questions.js` 可供离线网页直接读取。
