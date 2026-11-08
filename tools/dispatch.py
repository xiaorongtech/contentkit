#!/usr/bin/env python3
"""多渠道分发：用 agent-desktop 驱动已登录的浏览器发内容。

沙箱内读不到宿主窗口，所以这个脚本要在宿主权限下运行（一次调用完成整轮动作，
只需要一次授权）。用法：

  # 看当前页面结构（找 ref）
  python3 tools/dispatch.py snap --app chrome --grep 发布

  # 打开某个页面
  python3 tools/dispatch.py open --url https://x.com/compose/post

  # X 发帖（默认 dry-run：填好不点发送）
  python3 tools/dispatch.py x-post --text "内容…" [--send]

  # 截图存档
  python3 tools/dispatch.py shot --app chrome --out x-compose
"""
import argparse
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "content", "assets")


def ad(args, timeout=90):
    """调用 agent-desktop，返回解析后的 JSON。"""
    res = subprocess.run(["agent-desktop"] + args, capture_output=True, text=True, timeout=timeout)
    out = (res.stdout or "").strip()
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        sys.stderr.write((res.stderr or out)[-600:])
        raise SystemExit(f"agent-desktop 返回非 JSON: {' '.join(args[:2])}")
    if not data.get("ok", False):
        err = data.get("error", {})
        raise SystemExit(f"agent-desktop 失败: {err.get('code')} {err.get('message')}")
    return data


def focus(app):
    try:
        ad(["focus-window", "--app", app])
    except SystemExit:
        pass  # 有的环境焦点抢不过去，后续动作都用 --app 定向，照样能操作


def key(combo, app=None, headed=True):
    args = ["press", combo]
    if app:
        args += ["--app", app]
    if headed:
        args.append("--headed")
    ad(args)


def snapshot(app, grep=None, save=None):
    data = ad(["snapshot", "--app", app])
    text = json.dumps(data, ensure_ascii=False)
    if save:
        os.makedirs(os.path.dirname(save) or ASSETS, exist_ok=True)
        with open(save, "w") as f:
            f.write(json.dumps(data, ensure_ascii=False, indent=1))
    nodes = walk(data.get("data") or data)
    rows = []
    for n in nodes:
        label = " ".join(str(n.get(k, "")) for k in ("role", "name", "value", "text") if n.get(k))
        if not label.strip():
            continue
        ref = n.get("ref") or n.get("id")
        if grep and grep not in label:
            continue
        rows.append(f"{ref}\t{label[:110]}")
    return rows, text


def walk(node):
    stack = [node]
    while stack:
        cur = stack.pop()
        if isinstance(cur, dict):
            if any(k in cur for k in ("role", "ref")):
                yield cur
            for v in cur.values():
                if isinstance(v, (dict, list)):
                    stack.append(v)
        elif isinstance(cur, list):
            stack.extend(cur)


def matches(data):
    """find / snapshot 返回结构：{data: {matches: [...]}}"""
    d = data.get("data") or {}
    return d.get("matches") or []


def find(app, role=None, name=None):
    args = ["find", "--app", app]
    if role:
        args += ["--role", role]
    if name:
        args += ["--name", name]
    return matches(ad(args))


def cmd_snap(a):
    rows, _ = snapshot(a.app, grep=a.grep, save=a.save)
    print("\n".join(rows[:a.limit]))


def cmd_open(a):
    focus(a.app)
    key("ctrl+l", a.app)
    ad(["wait", "400"])
    key("ctrl+a", a.app)
    boxes = find(a.app, "textfield")
    target = None
    for b in boxes:
        if "地址" in str(b) or "ddress" in str(b) or "url" in str(b).lower():
            target = b
            break
    if target is None and boxes:
        target = boxes[0]
    if target is None:
        raise SystemExit("找不到地址栏")
    ref = target.get("ref_id") or target.get("ref")
    ad(["type", str(ref), a.url, "--app", a.app, "--headed"])
    key("return", a.app)
    ad(["wait", str(a.wait)])
    print(f"opened {a.url}")


def cmd_x_post(a):
    """X 发帖：打开编辑页 → 找到文本框 → 输入 → （可选）点发送。"""
    app = a.app
    focus(app)
    cmd_open(argparse.Namespace(app=app, url="https://x.com/compose/post", wait=3500))

    boxes = find(app, "textfield")
    target = None
    for b in boxes:
        blob = json.dumps(b, ensure_ascii=False).lower()
        if "post" in blob or "发帖" in blob or "tweet" in blob:
            target = b
            break
    if target is None and boxes:
        target = boxes[-1]
    if target is None:
        raise SystemExit("找不到发帖文本框（可能没登录或页面未加载）")

    ref = target.get("ref_id") or target.get("ref")
    ad(["type", str(ref), a.text, "--app", app, "--headed"])

    os.makedirs(ASSETS, exist_ok=True)
    shot = os.path.join(ASSETS, f"x-compose-{int(__import__('time').time())}.png")
    ad(["screenshot", shot, "--app", app])

    if not a.send:
        print(f"DRY-RUN 已填入，未发送。截图：{shot}")
        return

    btns = [b for b in find(app, "button") if "post" in json.dumps(b, ensure_ascii=False).lower()]
    if not btns:
        raise SystemExit(f"找不到发送按钮，草稿已填入。截图：{shot}")
    ad(["click", str(btns[0].get("ref_id") or btns[0].get("ref")), "--app", app, "--headed"])
    ad(["wait", "2500"])
    print(f"SENT 截图：{shot}")


def cmd_shot(a):
    os.makedirs(ASSETS, exist_ok=True)
    out = a.out if a.out.startswith("/") else os.path.join(ASSETS, a.out + ".png")
    ad(["screenshot", out, "--app", a.app])
    print(out)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("snap")
    s.add_argument("--app", default="chrome")
    s.add_argument("--grep")
    s.add_argument("--limit", type=int, default=60)
    s.add_argument("--save")
    s.set_defaults(func=cmd_snap)

    o = sub.add_parser("open")
    o.add_argument("--app", default="chrome")
    o.add_argument("--url", required=True)
    o.add_argument("--wait", type=int, default=3000)
    o.set_defaults(func=cmd_open)

    x = sub.add_parser("x-post")
    x.add_argument("--app", default="chrome")
    x.add_argument("--text", required=True)
    x.add_argument("--send", action="store_true")
    x.set_defaults(func=cmd_x_post)

    t = sub.add_parser("shot")
    t.add_argument("--app", default="chrome")
    t.add_argument("--out", required=True)
    t.set_defaults(func=cmd_shot)

    a = ap.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
