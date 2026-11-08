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

## 集成测试（接真实代码路径）

`tests/test_dispatch_fixture.py`（stdlib unittest，无依赖）：
把 `compose.html` 转成 dispatch.find 的 matches 树，喂给真实
`dispatch.py` 的 `find` / `snapshot` / `walk` 代码路径，断言能按
`role=textbox, name=Post text` 找到 ref-1。

```bash
python3 -m unittest tests.test_dispatch_fixture -v  # 3/3 通过
```
