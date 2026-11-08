# contentkit Roadmap

> 排序原则：按「别人用得上」排——陌生人 10 秒能看懂、30 秒能跑起来、跑完能复现，才算分。

## 1. 把 `dispatch.py` 浏览器分发写进 README（真实交付过的能力，现在是隐形）

- **现状**：`tools/dispatch.py`（213 行）是唯一让 contentkit 从「图文工具」变成「多平台分发」的模块：`snap/open/x-post --send/shot`，dry-run 默认不发送、发前截图存档，`--send` 才真正点发送。但 README 功能表（L29-38）没有这一行，正文 L8 只在 tagline 里提一嘴「浏览器分发」。别人扫 README 会把这项目归类为「又一个 Pillow 封面生成器」，直接错过核心差异点。
- **为什么别人用得上**：这是 contentkit 全部工具里唯一「别人用命令行做不到」的部分——imagetool 的 card/crop/mark，任何人都能用 ImageMagick 拼；dispatch 是把「写完文案 → 打开 X → 粘贴 → 发送」整条链路做成了可脚本化、可复现的命令。一个工具箱里最难复刻的那块，现在在 README 里是零行。
- **要做的事**：
  - 功能表加一行：`| 浏览器分发 | tools/dispatch.py x-post | 已登录浏览器自动填入发帖，默认 dry-run，--send 才发送 |`
  - 快速开始加 3 行 dispatch 示例（snap 找 ref → x-post dry-run → 截图存档），并明确写清前置条件：需宿主权限运行 + `agent-desktop` 已登录（沙箱内读不到宿主窗口，这一点 dispatch.py docstring 里已经写了，README 要原样同步过去，不要只在代码注释里）。
  - 把安全语义写成显式文案：「默认只是填好 + 截图，不点发送；加 `--send` 才发」——这是别人敢用的前提，不写就没人敢跑。
- **完成标志**：README 里 dispatch 有独立小节，不依赖跳进代码看 docstring。

## 2. README 的 `make_video` 示例同步到字幕入参（代码已支持，文档还在旧形）

- **现状**：`tools/make_video.py` 已支持每张图独立字幕：`--subtitle "顶栏|底栏"` 可重复（L28-63），顶栏 y=160、底栏 y=1780，时间窗按 `--per` 对齐。但 README L62-63 的示例停在无字幕旧形：
  `python3 tools/make_video.py --images cover.png content.png --out out.mp4`
  照着 README 跑，永远看不到字幕能力——而字幕正是幻灯片视频从「图拼起来」变成「可直接发抖音」的关键。
- **为什么别人用得上**：文档实例和代码不一致是开源项目最快的信任流失方式。别人 clone 下来照抄第一个例子跑通了、但得到的效果和 README 标题里承诺的（L36「多张卡片拼 1080×1920 视频 + 字幕」）对不上，就会觉得项目已废弃或偷懒，没人会去翻 `make_video.py` 源码才发现有 `--subtitle`。
- **要做的事**：
  - 把 L62-63 的例子改成带字幕的真实形（`--per 5 --subtitle "顶栏|底栏"` ×N），并补一句字幕时间窗规则：每张图对应一条 `--subtitle`，重复传 N 次，起止 `i*per+1 … (i+1)*per-1`。
  - 功能表 L36 的「+ 字幕（ffmpeg）」与新例子对齐；依赖说明里把 ffmpeg 和字体路径（`/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc`）写全——现在 README 只写了 ImageMagick + 字体，make_video 的 ffmpeg 在快速开始小字里才出现。
- **完成标志**：新人照抄 README 的 make_video 命令，能直接带字幕出包（本地已验证：card 生成、--help、语法均通过；ffmpeg/convert 均在本机可用）。

## 3. 按 ghfind 的「产品价值」结构重排 README 开头（10 秒懂、30 秒能跑）

- **现状**：README 结构是 tagline → 产品价值散文 → 功能表 → 视觉规范 → 快速开始。产品价值段（L14-25）说理充分，但没有 ghfind/minisearch 那种「动词清单 + 真实产出 + 一行安装」的高密度结构。ghfind 开头是 `Discover … — and become one.` + `What you can do` 五条动词 + 真实用户卡图片 + 安装/注册入口；minisearch 开头是 tagline + 零依赖 + 一键安装 + 在线 demo 分辨率。contentkit 现在的视觉规范（L40-43）排在功能表之后、快速开始之前——陌生人第一屏会先读到 `#FDF7EF` 的色值，而不是「这东西能替我做什么」。
- **为什么别人用得上**：工具出海拼的不是功能数量，是 README 第一屏的信息密度。别人不会读完 25 行说理才决定用不用；他们先在功能表里找自己的痛点，再看一张真实产出图决定要不要 clone。把视觉规范下移、把「能做什么」提上来，纯文档重排，零代码风险，收益最大。
- **要做的事**（只学结构，不抄文案）：
  - 顶部 tagline 后加 ghfind 式的 `What you can do`：5 条动词开头的清单（截窗口 / 裁重点 / 标步骤 / 出文字卡 / 拼带字幕视频 / dry-run 分发），每条带命令名——就是现有功能表的前移版。
  - 把 `examples/card-demo.png` 提为 hero 图（ghfind 把 `usercard.png` 放 tagline 之后就是这个用处），标题行紧跟 license badge。
  - 快速开始第一屏只放 card 一条命令（已有，L52-56），把 shot/crop/mark 往后挪到「进阶」；第一条命令要在无 agent-desktop 环境也能跑通（card 只依赖 ImageMagick），保证 30 秒出图。
  - 视觉规范 + 原则两节折叠或下移，放到快速开始之后。色值是给已有用户的，不该挡在新人的第一屏。
- **完成标志**：不读任何代码，10 秒内能回答「这是什么、给谁、我能用命令做出什么」；30 秒内第一条命令出图。

---

### 验证记录（本轮通读后实跑）

- `python3 tools/imagetool.py --help` / `make_video.py --help` / `dispatch.py --help`：三个工具均可正常解析参数。
- `python3 tools/imagetool.py card --kicker test --title 标题测试 --body 正文一行 --out /tmp/ck_test/cover`：成功生成 49K PNG（ffmpeg、convert 均在本机 `/usr/bin` 可用）。
- 四个工具文件 `ast.parse` 语法检查通过。
- `git log`：当前只有 1 个提交 `a9dbdf7`（v0.1 刚推），`docs/` 为空——本文件是 docs/ 下第一篇文档。
