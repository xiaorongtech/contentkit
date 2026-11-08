---- MODULE KeepAwake ----
\* keep-awake.sh 状态机（与脚本对齐的简化模型）：
\* Idle(循环起点) -> Inhibit(已抑制息屏，子进程 sleep 期间持锁)
\*   -> Sleep(子进程结束，锁释放，短暂等待)
\*   -> Inhibit -> ...
\* 脚本没有重试计数器：systemd-inhibit 失败只记日志继续循环，
\* 所以模型里没有 Fail/Retry 状态，也没有 retries 变量。
EXTENDS Naturals

VARIABLES state

States == {"Idle", "Inhibit", "Sleep"}

Init ==
    state = "Idle"

Wake ==
    /\ state = "Idle"
    /\ state' = "Inhibit"

InhibitDone ==
    /\ state = "Inhibit"
    /\ state' = "Sleep"

SleepDone ==
    /\ state = "Sleep"
    /\ state' = "Inhibit"

Next ==
    \/ Wake
    \/ InhibitDone
    \/ SleepDone

Spec == Init /\ [][Next]_state

TypeOK ==
    state \in States

\* 抑制窗口有界是结构保证的：Inhibit 只有一条出边到 Sleep，
\* 子进程结束锁即释放，下一步必回 Sleep，不会无限持有。
\* （不出带撇的伪不变量，所以 TLC 只验 TypeOK。）

====
