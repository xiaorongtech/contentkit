---- MODULE KeepAwake ----
\* keep-awake.sh 状态机：Idle -> Inhibit -> Sleep -> Inhibit...
\*                 Inhibit -> Fail -> Idle(重试)
\* retries 有界封顶 {0,1,2}，Fail 到顶保持，避免状态空间爆炸
EXTENDS Naturals

VARIABLES state, retries

States == {"Idle", "Inhibit", "Sleep", "Fail"}
RetryVals == {0, 1, 2}

Init ==
    /\ state = "Idle"
    /\ retries = 0

Wake ==
    /\ state = "Idle"
    /\ state' = "Inhibit"
    /\ retries' = retries

InhibitDone ==
    /\ state = "Inhibit"
    /\ state' = "Sleep"
    /\ retries' = retries

SleepDone ==
    /\ state = "Sleep"
    /\ state' = "Inhibit"
    /\ retries' = retries

Fail ==
    /\ state = "Inhibit"
    /\ state' = "Fail"
    /\ retries' = IF retries < 2 THEN retries + 1 ELSE retries

Retry ==
    /\ state = "Fail"
    /\ state' = "Idle"
    /\ retries' = retries

Next ==
    \/ Wake
    \/ InhibitDone
    \/ SleepDone
    \/ Fail
    \/ Retry

Spec == Init /\ [][Next]_<<state, retries>>

TypeOK ==
    state \in States /\ retries \in RetryVals

FailHasRetries ==
    state = "Fail" => retries > 0

====
