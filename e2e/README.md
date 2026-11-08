# e2e 回归

dispatch.py 的浏览器分发三链路（snap 找 ref → x-post dry-run 只填不发 → shot 截图存档）用 tester-army/e2e 回归。

## 真跑报告（2026-11-08）
- `npx e2e` v0.23.0，`@e2e-dev/web` chromium-headless-shell
- 4/4 通过，3.53s：snap 定位、example、dry-run 不发送、shot
- fixture 是本地 compose 页（无模型调用，--gateway none）

## 跑
```bash
node fixtures/server.mjs &  # 127.0.0.1:8901
PLAYWRIGHT_BROWSERS_PATH=$PWD/.browsers APP_URL=http://127.0.0.1:8901 npx e2e run
```
首次只有 npx 拉浏览器。真实 X 页不放 e2e，真实链路走 dispatch.py 自身 dry-run。
