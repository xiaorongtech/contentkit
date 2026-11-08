<div align="center">

# contentkit

**Markdown 一行命令，出一整套多平台图文/视频素材。**

自媒体人把「写完文案之后」的那段时间压缩到零：
截图、裁剪、标注、文字卡、幻灯片视频、飞书通知、浏览器分发——一个工具箱搞定。

[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)

</div>

## 产品价值

自媒体人做内容，时间往往不是花在写作上，而是花在**收尾**上：

- 写完文案，要配图 → 打开 PS 拼一小时
- 需要一张「重点圈出来」的截图 → 手动截、手动画框
- 要发抖音图文 → 又要排版一遍
- 每天要给自己汇报数据 → 手动翻后台记数

这些活儿重复、琐碎、吃掉创作时间。contentkit 把它们做成命令行，让你**只做决定，剩下给脚本**。

**给谁**：独立创作者、小团队运营、AI 工具博主、需要批量产出图文的任何人。

## 功能

| 能力 | 命令 | 解决什么 |
|---|---|---|
| 应用窗口截图 | `imagetool.py shot --app Feishu` | 比全屏截图有价值得多，只截关键窗口 |
| 裁剪聚焦 | `imagetool.py crop --box x,y,w,h` | 只留关键区域，信息密度翻倍 |
| 重点标注 | `imagetool.py mark` | 红框 + 编号 + 箭头，步骤图一目了然 |
| 文字卡 | `imagetool.py card --size xhs` | 小红书 3:4 / X 方图 / 竖版故事，一条命令出图 |
| 素材登记 | `imagetool.py log` | 提示词/抽卡次数/是否采用，自动记 CSV 复盘 |
| 幻灯片视频 | `tools/make_video.py` | 多张卡片拼 1080×1920 视频 + 字幕（ffmpeg） |
| 飞书通知 | `tools/notify_feishu.py` | 定时把运营情况推到飞书卡片 |
| 看门狗 | `tools/keep-awake.sh` | systemd 服务，每 5 分钟防息屏锁屏 |

## 视觉规范（固定，不换）

暖米纸底 `#FDF7EF`、墨字 `#2B2B2B`、暖橘强调 `#E8734A`、细线 `#E6DCD0`。
一套配色用到底，就是账号的辨识度——不要每张换风格。

## 快速开始

```bash
git clone https://github.com/xiaorongtech/contentkit.git
cd contentkit

# 依赖：Python 3 + ImageMagick（convert）+ 中文字体 Noto Sans CJK
python3 tools/imagetool.py card \
  --kicker "AI 实测 #01" \
  --title "标题最多两行" \
  --body "正文 3-5 行" \
  --footer "@你的账号" --out cover

python3 tools/imagetool.py shot --app Feishu --out feishu-ui
python3 tools/imagetool.py crop --in feishu-ui.png --box 300,200,800,500 --out focus
python3 tools/imagetool.py mark --in focus.png --out marked --box "40,20,300,80,1"

# 幻灯片视频（ffmpeg）
python3 tools/make_video.py --images cover.png content.png --out out.mp4
```

## 示例

`examples/` 里有真实产出的卡片和截图，全部由本工具生成。

![card demo](examples/card-demo.png)

## 原则

- **图是加分项，不是必需品**：凑数的图不放
- **截图优先于生图**：界面、数据、对比靠截图，不靠 AI 生成
- **生图只做插画**（动画/卡通/手绘），禁止生成真人真场景
- **内容只放大别人的价值**：不炫技，不晒自己的工作流

## License

MIT
