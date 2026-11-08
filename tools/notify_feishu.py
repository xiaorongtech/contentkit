#!/usr/bin/env python3
"""给用户发飞书卡片通知。

用法:
  python3 notify_feishu.py --title "标题" --body "markdown 正文"
  python3 notify_feishu.py --title "标题" --body "$(cat report.md)"
  python3 notify_feishu.py --test
"""
import argparse
import json
import os
import sys
import urllib.request

APP_ID = os.environ.get("FEISHU_APP_ID", "cli_aa673f8fdbb81d0b")
CHAT_ID = os.environ.get("FEISHU_CHAT_ID", "oc_9173f1c221b044275e50a7604d59df17")
BASE = "https://open.feishu.cn"
SECRET = os.environ.get("DSH_SECRET_FEISHU_APP_SECRET", "")


def post(url, payload, token=None):
    headers = {"content-type": "application/json"}
    if token:
        headers["authorization"] = f"Bearer {token}"
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(), headers=headers, method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def tenant_token():
    body = post(
        f"{BASE}/open-apis/auth/v3/tenant_access_token/internal",
        {"app_id": APP_ID, "app_secret": SECRET},
    )
    if body.get("code") != 0:
        raise SystemExit(f"get token failed: {body.get('code')} {body.get('msg')}")
    return body["tenant_access_token"]


def card(title, body):
    return {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": title},
            "template": "blue",
        },
        "elements": [
            {"tag": "div", "text": {"tag": "lark_md", "content": body}},
            {"tag": "hr"},
            {
                "tag": "note",
                "elements": [{"tag": "plain_text", "content": "内容生产线 · 自动汇报"}],
            },
        ],
    }


def send(title, body):
    token = tenant_token()
    payload = {
        "receive_id": CHAT_ID,
        "msg_type": "interactive",
        "content": json.dumps(card(title, body), ensure_ascii=False),
    }
    res = post(
        f"{BASE}/open-apis/im/v1/messages?receive_id_type=chat_id", payload, token
    )
    if res.get("code") != 0:
        raise SystemExit(f"send failed: {res.get('code')} {res.get('msg')}")
    return res["data"]["message_id"]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", default="内容生产线日报")
    ap.add_argument("--body", default="")
    ap.add_argument("--test", action="store_true")
    args = ap.parse_args()

    if not SECRET:
        raise SystemExit("DSH_SECRET_FEISHU_APP_SECRET is empty")

    if args.test:
        title = "通知链路已接通"
        body = "以后每天 18:00 我会用这张卡片发当天运营情况。\n\n这是一条测试消息。"
    else:
        title = args.title
        body = args.body or "（空）"

    mid = send(title, body)
    print(f"sent message_id={mid}")
