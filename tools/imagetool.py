#!/usr/bin/env python3
"""内容配图工具：截图 / 裁剪聚焦 / 标注重点 / 文字卡 / 素材登记。

依赖：ImageMagick(convert) + agent-desktop。全部走命令行，不装额外库。

常见用法
  # 1. 截某个应用的窗口（比全屏有价值）
  python3 tools/imagetool.py shot --app Feishu --out content/assets/feishu-ui

  # 2. 只留关键区域：坐标 x,y,宽,高
  python3 tools/imagetool.py crop --in a.png --box 120,300,860,420 --out a-focus

  # 3. 标注重点：红框 + 编号 + 箭头
  python3 tools/imagetool.py mark --in a-focus.png --out a-marked \
      --box "40,20,300,80,1" --box "40,120,300,80,2"

  # 4. 纯文字卡（小红书 3:4 / X 方图 / 竖版故事）
  python3 tools/imagetool.py card --title "标题" --body "正文…" --size xhs --out cover

  # 5. 登记到 content/data/images.csv
  python3 tools/imagetool.py log --file cover.png --use 小红书封面 --source card \
      --prompt "无需生图" --tries 1 --adopted yes

所有图片默认落在 content/assets/，输出统一 PNG，宽度超过 max-width 自动缩放。
"""
import argparse
import csv
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "content", "assets")
DATA = os.path.join(ROOT, "content", "data")
IMAGES_CSV = os.path.join(DATA, "images.csv")

FONT = "Noto-Sans-CJK-SC"
FONT_BOLD = "Noto-Sans-CJK-SC-Bold"

PAPER = "#FDF7EF"      # 暖米色纸面
INK = "#2B2B2B"        # 墨色正文
ACCENT = "#E8734A"     # 暖橘强调
MUTED = "#8A817C"      # 次要信息
LINE = "#E6DCD0"       # 细线

SIZES = {"xhs": (1080, 1440), "square": (1080, 1080), "story": (1080, 1920)}


def run(cmd):
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        sys.stderr.write((res.stderr or res.stdout)[-800:])
        raise SystemExit(f"命令失败: {' '.join(cmd[:3])}…")
    return res.stdout


def ensure_dirs():
    os.makedirs(ASSETS, exist_ok=True)
    os.makedirs(DATA, exist_ok=True)


def target(path, ext=".png"):
    if os.path.isabs(path) or "/" in path:
        out = path if path.endswith(ext) else path + ext
    else:
        out = os.path.join(ASSETS, path if path.endswith(ext) else path + ext)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    return out


def wrap(text, per_line):
    """按显示宽度折行：中文按 1 个字宽，英文数字按 0.55。"""
    lines, cur, width = [], "", 0.0
    for ch in text:
        w = 1.0 if ord(ch) > 0x2E80 else 0.55
        if ch == "\n":
            lines.append(cur)
            cur, width = "", 0.0
            continue
        if width + w > per_line:
            lines.append(cur)
            cur, width = ch, w
        else:
            cur += ch
            width += w
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- commands
def cmd_shot(args):
    ensure_dirs()
    out = target(args.out)
    cmd = ["agent-desktop", "screenshot", out]
    if args.app:
        cmd += ["--app", args.app]
    if args.window_id:
        cmd += ["--window-id", args.window_id]
    if args.screen is not None:
        cmd += ["--screen", str(args.screen)]
    run(cmd)
    if args.max_width:
        run(["convert", out, "-resize", f"{args.max_width}x>", out])
    print(out)


def cmd_crop(args):
    src = os.path.abspath(args.input)
    out = target(args.out)
    x, y, w, h = (int(v) for v in args.box.split(","))
    run(["convert", src, "-crop", f"{w}x{h}+{x}+{y}", "+repage", out])
    if args.max_width:
        run(["convert", out, "-resize", f"{args.max_width}x>", out])
    print(out)


def cmd_mark(args):
    src = os.path.abspath(args.input)
    out = target(args.out)
    draws, labels = [], []

    for spec in args.box or []:
        parts = spec.split(",")
        x, y, w, h = (int(v) for v in parts[:4])
        tag = parts[4] if len(parts) > 4 else ""
        # 先描一层浅色衬底，再描主色，避免深色背景上看不清
        draws.append(f"fill none stroke white stroke-width 9 rectangle {x},{y} {x+w},{y+h}")
        draws.append(f"fill none stroke {ACCENT} stroke-width 5 rectangle {x},{y} {x+w},{y+h}")
        if tag:
            bx, by = x - 6, max(0, y - 34)
            draws.append(f"fill {ACCENT} stroke none roundrectangle {bx},{by} {bx+34},{by+34} 8,8")
            labels.append((bx + 8, by + 26, tag, "white", 26))

    for spec in args.arrow or []:
        x1, y1, x2, y2 = (int(v) for v in spec.split(","))
        draws.append(f"fill none stroke white stroke-width 9 line {x1},{y1} {x2},{y2}")
        draws.append(f"fill {ACCENT} stroke none polygon {x2},{y2} {x2-16},{y2-6} {x2-6},{y2-16}")

    for spec in args.note or []:
        x, y, text = spec.split(",", 2)
        labels.append((int(x), int(y), text, INK, 30))

    cmd = ["convert", src, "-strokewidth", "5", "-draw", " ".join(draws)] if draws else ["convert", src]
    for x, y, text, color, size in labels:
        cmd += ["-stroke", "none", "-font", FONT_BOLD, "-pointsize", str(size), "-fill", color,
                "-annotate", f"+{x}+{y}", text]
    cmd.append(out)
    run(cmd)
    print(out)


def cmd_card(args):
    ensure_dirs()
    out = target(args.out)
    width, height = SIZES.get(args.size, SIZES["xhs"]) if isinstance(args.size, str) else (
        int(args.size.split("x")[0]), int(args.size.split("x")[1]))
    margin = int(width * 0.09)
    inner = width - margin * 2

    blocks = []  # (kind, lines, pointsize, color, gap_before)

    if args.kicker:
        blocks.append(("kicker", [args.kicker], 30, MUTED, 0))
    if args.title:
        size = args.title_size or int(width * 0.075)
        blocks.append(("title", wrap(args.title, inner // size), size, INK, 34))
    if args.body:
        size = int(width * 0.042)
        blocks.append(("body", wrap(args.body, inner // size), size, "#4A4340", 40))
    if args.footer:
        blocks.append(("footer", wrap(args.footer, inner // 28), 28, MUTED, 60))

    total = 0
    for _, lines, size, _, gap in blocks:
        total += gap + len(lines) * int(size * 1.55)
    y = margin if total > height - margin * 2 else max(margin, (height - total) // 2)

    cmd = ["convert", "-size", f"{width}x{height}", f"xc:{PAPER}",
           "-fill", "none", "-stroke", LINE, "-strokewidth", "3",
           "-draw", f"roundrectangle {margin//2},{margin//2} {width-margin//2},{height-margin//2} 28,28",
           "-stroke", "none"]

    for kind, lines, size, color, gap in blocks:
        y += gap
        if kind == "kicker":
            cmd += ["-font", FONT_BOLD, "-pointsize", str(size), "-fill", ACCENT,
                    "-annotate", f"+{margin}+{y + size}", lines[0]]
            y += int(size * 1.55)
            continue
        for line in lines:
            cmd += ["-font", FONT_BOLD if kind == "title" else FONT, "-pointsize", str(size),
                    "-fill", color, "-annotate", f"+{margin}+{y + size}", line]
            y += int(size * 1.55)
        if kind == "title":
            # 标题下一道强调短线
            cmd += ["-fill", ACCENT, "-stroke", "none",
                    "-draw", f"rectangle {margin},{y + 6} {margin + 96},{y + 14}"]
            y += 26

    if args.tag:
        cmd += ["-font", FONT, "-pointsize", str(int(width * 0.032)), "-fill", MUTED,
                "-annotate", f"+{width - margin - len(args.tag) * int(width * 0.032)}+{height - margin - 12}", args.tag]

    cmd.append(out)
    run(cmd)
    print(out)


def cmd_log(args):
    ensure_dirs()
    new = not os.path.exists(IMAGES_CSV)
    with open(IMAGES_CSV, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["date", "file", "use", "source", "prompt", "tries", "adopted", "note"])
        w.writerow([time.strftime("%Y-%m-%d"), os.path.basename(args.file), args.use, args.source,
                    args.prompt, args.tries, args.adopted, args.note])
    print(IMAGES_CSV)


def main():
    ap = argparse.ArgumentParser(description="内容配图工具")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("shot", help="截应用窗口")
    s.add_argument("--app")
    s.add_argument("--window-id")
    s.add_argument("--screen", type=int)
    s.add_argument("--max-width", type=int, default=1400)
    s.add_argument("--out", required=True)
    s.set_defaults(func=cmd_shot)

    c = sub.add_parser("crop", help="裁剪聚焦区域 x,y,w,h")
    c.add_argument("--in", dest="input", required=True)
    c.add_argument("--box", required=True)
    c.add_argument("--max-width", type=int, default=1400)
    c.add_argument("--out", required=True)
    c.set_defaults(func=cmd_crop)

    m = sub.add_parser("mark", help="标注重点")
    m.add_argument("--in", dest="input", required=True)
    m.add_argument("--box", action="append", help="x,y,w,h[,编号]")
    m.add_argument("--arrow", action="append", help="x1,y1,x2,y2")
    m.add_argument("--note", action="append", help="x,y,文字")
    m.add_argument("--out", required=True)
    m.set_defaults(func=cmd_mark)

    k = sub.add_parser("card", help="生成文字卡")
    k.add_argument("--kicker")
    k.add_argument("--title")
    k.add_argument("--title-size", type=int)
    k.add_argument("--body")
    k.add_argument("--footer")
    k.add_argument("--tag", default="")
    k.add_argument("--size", default="xhs", help="xhs|square|story|1080x1440")
    k.add_argument("--out", required=True)
    k.set_defaults(func=cmd_card)

    g = sub.add_parser("log", help="登记素材")
    g.add_argument("--file", required=True)
    g.add_argument("--use", default="")
    g.add_argument("--source", default="screenshot", choices=["screenshot", "card", "ai", "photo"])
    g.add_argument("--prompt", default="")
    g.add_argument("--tries", type=int, default=1)
    g.add_argument("--adopted", default="yes", choices=["yes", "no"])
    g.add_argument("--note", default="")
    g.set_defaults(func=cmd_log)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
