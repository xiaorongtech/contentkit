# TLA 建模

`keep-awake.sh` 调度状态机（tools/keep-awake.sh 之前只写在 README 表里、文件不存在，本轮已补）。

## 模型
KeepAwake.tla：Idle -> Inhibit（抑制息屏）-> Sleep（间隔计时）-> Inhibit…
失败分支 Inhibit -> Fail -> Idle（重试）。retries 有界 {0,1,2} 封顶避免状态空间爆炸。

## 真跑（2026-11-08，tla-ts check）
- TypeOK: success
- FailHasRetries: success

注：初版 DropInvariant 写错（要求终身 Idle/Fail），首步 Wake 就违例，那是模型错不是脚本错，已改正并记录教训。
