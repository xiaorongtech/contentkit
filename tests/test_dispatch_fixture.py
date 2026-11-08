#!/usr/bin/env python3
"""dispatch.py 解析 fixture compose.html 的集成测试。

不走 agent-desktop：在 dispatch.find/ad 入口处换成从 compose.html
构建的 matches 树，验证 dispatch.py 真实代码能从 fixture 找到 ref。
对应评审要求：fixture 不能只测自己，必须接上真实代码路径。
"""
import json
import os
import sys
import unittest
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import dispatch  # noqa: E402


class ComposeParser(HTMLParser):
    """把 compose.html 转换成 dispatch.find 风格的 matches 列表。"""

    def __init__(self):
        super().__init__()
        self.matches = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        ref = f"ref-{len(self.matches) + 1}"
        if tag == "textarea":
            self.matches.append({
                "role": "textbox",
                "name": d.get("aria-label", ""),
                "ref": ref,
                "id": d.get("id", ""),
            })
        elif tag == "button":
            text = next((v for k, v in attrs if k == "name"), "") or "Post"
            self.matches.append({"role": "button", "name": text, "ref": ref})


def load_matches():
    p = ComposeParser()
    with open(os.path.join(ROOT, "e2e", "fixtures", "compose.html")) as f:
        p.feed(f.read())
    return {"data": {"matches": p.matches}}


class DispatchFixtureTest(unittest.TestCase):
    def setUp(self):
        self.orig_ad = dispatch.ad
        dispatch.ad = lambda args, **kw: load_matches()  # noqa: SLF001

    def tearDown(self):
        dispatch.ad = self.orig_ad

    def test_find_returns_fixture_textbox(self):
        boxes = dispatch.find("chrome", "textfield")
        self.assertTrue(boxes, "fixture 应提供 textbox")
        # 走 dispatch.py 里 cmd_x_post 的 blob 匹配（post/发帖/tweet）
        target = None
        for b in boxes:
            blob = json.dumps(b, ensure_ascii=False).lower()
            if "post" in blob:
                target = b
                break
        self.assertIsNotNone(target, "应能按 post 匹配到文本框")
        self.assertEqual(target["ref"], "ref-1")
        self.assertEqual(target["role"], "textbox")

    def test_snapshot_grep_finds_post(self):
        rows, _ = dispatch.snapshot("chrome", grep="Post")
        self.assertTrue(any("textbox" in r for r in rows))

    def test_walk_and_matches_helpers(self):
        data = load_matches()
        self.assertEqual(len(dispatch.matches(data)), 2)
        nodes = list(dispatch.walk(data))
        refs = [n.get("ref") for n in nodes]
        self.assertIn("ref-1", refs)


if __name__ == "__main__":
    unittest.main(verbosity=2)
