# TLA 建模

`keep-awake.sh` 调度状态机（tools/keep-awake.sh 之前只写在 README 表里、文件不存在，本轮已补）。

## 模型
KeepAwake.tla：Idle -> Inhibit（抑制息屏，子进程 sleep 期间持锁）-> Sleep（锁释放，短暂等待）-> Inhibit…
脚本里没有失败计数和重试状态机（失败只记日志继续循环），模型不虚构 Fail/Retry 两档，retries 已删掉。

## 真跑（2026-11-08，tla-ts check）
- TypeOK: success

## 评审回炉（同日已改）
- 修脚本：删掉 inhibit 之后的外层 sleep INTERVAL（原来抑制窗口 300 秒，外部又睡 300 秒，实际保护间隔跑到 600 秒，中间断 300 秒空档）。现在 systemd-inhibit 子进程本身就是计时器。
- TLA 对齐脚本：去掉 Fail/Retry/retries，与 while 循环一致；抑制窗口有界是结构保证（Inhibit 只有一条出边到 Sleep）。
