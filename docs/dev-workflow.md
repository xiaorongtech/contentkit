# 开发流程

四个外部组件如何进我们的开发流程。顺序固定：纪律 → 图谱 → 回归 → 建模。

## 1. pstack 规范层（poteto / cursor/plugins）

纪律全部来自 [poteto-mode](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/SKILL.md) 本会话已读全文。本地执行派生出以下几条，立即生效：

- **一次一事，一事一验**：一个任务只做一件事，每个改动以可验证状态收尾。序列本身要证明自己。
- **深挖再并行**：先把数据形状定好（比如 contentkit 的状态机、图谱结构），再起并行工人。形状不定，并行只会产出格式不同的垃圾。
- **少写但高质量（Laziness Protocol）**：偏向删除和最小改动。README 里 keep-awake.sh 只写在表里、文件不存在，就是这种债：先补文件再谈别的。
- **证明它能跑（Prove It Works）**：每个完成声明都要跑真产物验证。`/help` 不算，跑出图、出 mp4、跑出 e2e 报告才算。
- **修根因不修症状（Fix Root Causes）**：每个症状追到第一处出错位。guard 只有当处理的是合法状态时才算修复。
- **测试行为不测试实现**：断言用户可观测的行为。内部改动不让测试变红。
- **自主推进（Never Block on Human）**：可逆的活儿直接做，做完让 Chief 纠正。不可逆的操作才暂停。
- **review 清单**：每次交付前过 `no-comments`（删无谓注释）、`unslop`（删废话）、`technical-writing`（Diátaxis + Google 风格）三道。commit 信息写 why，不写 what。

## 2. Graphify 知识图谱（Graphify-Labs/graphify）

把代码库转成可查询的知识图谱，架构和依赖关系进知识库。

```bash
# 安装（PyPI 包名暂时为 graphifyy，命令仍为 graphify）
uv tool install graphifyy   # 或 pip install graphifyy
graphify install            # 注册 /graphify 技能
```

用法：
- `graphify .`：在本仓库根跑，产出 `graphify-out/`（graph.html、GRAPH_REPORT.md、graph.json、缓存）。
- `graphify query "dispatch 和数据库有什么关系"`：查图谱代替翻代码。
- `graphify hook install`：每次 commit 后自动重建图谱。

`GRAPH_REPORT.md` 里有 god nodes（最核心概念）和 surprising connections，查 contentkit 架构时先读它。

我们怎么用：contentkit 每次有结构性改动（新增工具、改分发链路）后，commit 后跑一遍 `/graphify`。报告落仓库里，别人 clone 就能看懂系统怎么搭的。

## 3. tester-army/e2e 回归（浏览器分发）

contentkit 的浏览器分发（dispatch.py）和 X/小红书发布流程目前是手动 CDP 连的，升格成 e2e 回归。

```bash
npx e2e init   # 选 web 引擎 + 模型 provider，生成配置和示例测试
```

测试形态：自然语言描述目标，agent 驱动浏览器，locator + assertion 验结果。同一次测试里既下指令又断言。

我们怎么用：dispatch.py 的三条链路（snap 找 ref → x-post dry-run → 截图存档）各写一个 e2e。dry-run 是默认的，确保回归永不真发。agent 步骤记录后可无模型回放，CI 里跑得起。

注意：本机无 pip 时 e2e 侧完全走 npx/node，不受 Python 环境影响。

## 4. tla-ts 形式化建模（aidenybai/tla-ts）

TLA+ 模型检查，TLC 的 JS 替代品，免 JVM。`npm install tla-ts`，`npx tla-ts Spec.tla`。

```ts
import { check } from "tla-ts";
const result = await check({ source, config: "INIT Init NEXT Next INVARIANT Small" });
result.status; // "success" | "deadlock" | "invariant-violation" ...
```

我们怎么用：看门狗调度状态机（`tools/keep-awake.sh`：运行 → 抑制息屏 → 间隔计时 → 醒来复检 → 失败重试 → 退出）、dispatch 的并发分发逻辑，先建模跑一遍再上线。模型里写不变量（比如「抑制窗口和锁屏窗口永不重叠失效」），violations 出 trace，直接看哪条路径坏。

每项目标产物对照：
- README（产品价值结构）← roadmap 1→2→3 顺序改
- docs/roadmap ← 排序依据
- e2e 回归 ← dispatch 三条链路
- 知识图谱 ← graphify-out/GRAPH_REPORT.md
- ghfind 收录条件 ← 清晰的 README + 可跑的安装/命令/测试，ghfind 只吃 public GitHub 数据
