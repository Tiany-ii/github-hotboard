# GitHub Hotboard

**一个跑在本地桌面的 GitHub 热榜看板：今天该看什么，一屏看完。**

[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%2010%2B-0078d4.svg)](#系统要求)
[![No telemetry](https://img.shields.io/badge/telemetry-none-brightgreen.svg)](#数据来源与隐私)

![GitHub Hotboard](docs/images/list.png)

> English version: [README.md](README.md)

---

## 这是什么

GitHub Hotboard 是一个完全跑在本机的桌面看板。它拉取 GitHub 的热榜，追踪你关注的项目，
并让你不用离开程序就能判断一个项目值不值得投入——双语 README、增长曲线，以及一张会参考
star、issue 和维护活跃度的 AI 总结卡。

**它解决什么。** GitHub 自己的 Trending 只给一个列表，不告诉你涨得多快、还在不在维护、
这个项目到底干什么。Hotboard 把这些判断所需的信息放在同一屏，并缓存到本地，第二次打开
不用等。

**它不做什么。** 不做账号、不做推荐算法、不上传任何使用数据、不替你 star 或 fork。所有
请求直接发往 GitHub 官方接口。

---

## 截图

<details>
<summary>项目详情：双语 README、指标、增长曲线</summary>

![详情](docs/images/detail.png)

</details>

<details>
<summary>每日简报：一天一页，自动换新</summary>

![简报](docs/images/brief.png)

</details>

<details>
<summary>深色主题</summary>

![深色](docs/images/dark.png)

</details>

---

## 核心特性

- **五个榜单 + 每日简报。** 全站热榜、新项目、分类精选、DeepSeek 插件生态、我的榜单。
  简报把当天信息滚成一页，每天早上自动换新。
- **关注项目的变动提醒。** Star 涨跌、新提交、issue 突增、90 天未更新。**零额外 API 调用**
  ——它比的是打开榜单时本来就拉到的数据。
- **双语 README。** 原文 / 双语对照 / 仅中文三档，按段对齐，不是整篇机翻。
- **AI 总结卡。** 除了 README，模型还能看到 star、fork、未关闭 issue、最近推送和许可证，
  所以能说出「8 个月没提交但积压 1,200 个 issue，维护可能停滞」这类 README 里没有的判断。
- **一键下载。** 列出 Release 资产与源码 ZIP 并说明区别，选目录、看进度，源码自动解压，
  不覆盖同名文件夹。
- **本地优先。** 无账号、无遥测。数据存在 WebView2 配置目录；便携模式下跟着 exe 走，
  整个文件夹拷到别的电脑，关注列表也一起过去。
- **模型与 Key 自选。** 可存多个 DeepSeek Key 随时切换；模型可选 `deepseek-flash` 或
  `deepseek-v4-pro`，思考模式单独开关。
- **细节到位。** 深浅色主题、键盘可达（Tab 到行、回车打开）、断网时保留上次数据并标红连接状态。

---

## 系统要求

- **Windows 10 或更高**（x64）。macOS 与 Linux 暂不支持。
- **WebView2 运行时** —— Windows 11 和较新的 Windows 10 已自带。如果窗口空白，
  去 [微软官网](https://developer.microsoft.com/microsoft-edge/webview2/) 装一次。
- 使用预编译 exe 不需要装 Python。

---

## 快速开始

1. 从 [Releases](../../releases) 下载最新的 `GitHub-Hotboard-*-win-x64.zip`，解压到任意目录。
2. 双击 `GitHub Hotboard.exe`。

> **首次运行会被 SmartScreen 拦一下**（「Windows 已保护你的电脑」），因为 exe 没有代码签名。
> 点 **更多信息 → 仍要运行**。如果你不想信任二进制文件，可以按下面的方式从源码运行。

**便携模式。** 在 exe 同级放一个名为 `portable.txt` 的文件（或一个 `data` 文件夹），
所有设置、关注列表和缓存都会写进 `./data`，而不是 `%LOCALAPPDATA%`。

---

## 使用

完整说明在 [`docs/使用说明.html`](docs/使用说明.html)，用浏览器打开即可。最常用的五个动作：

| 我想…… | 怎么做 |
|---|---|
| 看今天有什么火的 | 打开就是，第一个标签自动加载 |
| 判断一个项目值不值得花一周 | 点一行 → 看 AI 总结卡 |
| 用中文读 README | 详情页 → **翻译**（需要 DeepSeek Key，或走免费引擎） |
| 追一个项目 | 详情页 → **加入我的榜单** |
| 下载 release 或源码 | 详情页 → **下载** |

可选：在「关于」页填一个 DeepSeek API Key，开启 AI 总结和更高质量的翻译。不填也能用，
会退回免费翻译服务（每天有额度限制）。

---

## 数据来源与隐私

全部在本机运行，没有后端、没有统计、没有崩溃上报。

| 服务 | 用途 | 说明 |
|---|---|---|
| `api.github.com` | 全部仓库数据 | 公开 REST API；未登录 60 次/小时，填 Token 后 5,000 次/小时 |
| `codeload.github.com` | 下载源码 ZIP | 只在你点下载时请求 |
| `api.deepseek.com` | AI 总结、翻译 | 只有你自己填了 Key 才会用 |
| `api.mymemory.translated.net` | 免费翻译兜底 | 匿名额度约 5,000 字符/天/IP |
| `api.star-history.com` | 第三方增长曲线图片 | 以图片形式嵌入，挂掉不影响主流程 |
| `awesome-dsh-plugin.com` | DeepSeek 插件目录 | 第三方 JSON，不可用时优雅降级 |

**本地存了什么：** 关注列表、译文与总结缓存、下载记录，以及你自己填的 API Key。全部在
WebView2 配置目录（`%LOCALAPPDATA%\GitHubHot`，便携模式为 `./data`），除了上面这些请求，
不会离开你的电脑。

**Key 不会进备份。** 导出的备份文件刻意剔除了 DeepSeek Key 和 GitHub Token。

---

## 从源码运行

```bash
git clone https://github.com/<you>/github-hotboard.git
cd github-hotboard
python -m pip install -r requirements.txt
python app.py
```

也可以直接用浏览器打开 `github-hot.html`——除了下载按钮（会降级成浏览器下载）和原生
文件夹选择框，其余功能都正常。

常用参数：

```bash
python app.py --version      # 打印版本
python app.py --where        # 打印数据存储位置
python app.py --selftest     # 无界面自检：服务 + 页面加载
python app.py --selftest-dl  # 无界面自检：下载 + 解压
python app.py --reset        # 给损坏的 WebView2 配置改名（保留数据）
python app.py --debug        # 打开开发者工具
```

---

## 构建

```bash
python -m pip install -r requirements.txt
python build.py            # 或双击 build.bat
```

产物在 `dist/GitHub Hotboard.exe`（约 13 MB，单文件）。

> WebView2 的 .NET 程序集必须放在 PyInstaller 归档的**根目录**，否则窗口会白屏。
> `build.py` 已经处理好了，别删那几行 `--add-binary`。

---

## 项目结构

```
github-hotboard/
├─ app.py              # 桌面外壳：本地 HTTP 服务、窗口、下载器、命令行参数
├─ github-hot.html     # 整个界面：HTML + CSS + JS 单文件，无构建步骤
├─ build.py            # PyInstaller 打包
├─ build.bat           # Windows 一键包装
├─ app.ico
├─ requirements.txt
├─ docs/
│  ├─ 使用说明.html     # 用户手册
│  ├─ 更新记录.txt      # 详细更新流水（每次改动都记）
│  ├─ CHANGELOG.md     # 版本级摘要（Keep a Changelog）
│  └─ images/          # README 用到的截图
└─ LICENSE
```

界面刻意做成零依赖的单文件：改一行样式刷新就能看到结果。代价是文件很大，见下。

---

## 已知限制

- **仅支持 Windows。** 外壳依赖 WebView2、`os.startfile` 和 `%LOCALAPPDATA%`。
- **界面是一个 200 KB 的 HTML 单文件。** 没有打包器、没有模块化。贡献门槛极低，但大规模
  重构会比较吃力。
- **没有自动化测试与 CI。** 目前靠手工验证加 `--selftest*` 参数。
- **没有自动更新。** 需要手动下载新版本。
- **二进制未签名。** 首次运行会有 SmartScreen 提示。
- **受 GitHub 接口限额约束。** 未登录 60 次/小时，在程序里填 Token 可提到 5,000 次/小时。

---

## 许可证

[MIT](LICENSE)。

本项目为非官方项目，与 GitHub, Inc. 无关联、未获其背书或赞助。
「GitHub」是 GitHub, Inc. 的注册商标。

---

## 致谢

- [star-history.com](https://star-history.com) —— 增长曲线图片
- [awesome-dsh-plugin.com](https://awesome-dsh-plugin.com) —— DeepSeek 插件目录
- [MyMemory](https://mymemory.translated.net) —— 免费翻译兜底
- [DeepSeek](https://platform.deepseek.com) —— AI 总结与翻译
- [pywebview](https://pywebview.flowrl.com) —— 桌面外壳
