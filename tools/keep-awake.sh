#!/usr/bin/env bash
# keep-awake.sh: 每 5 分钟防息屏锁屏（systemd 服务配合）
# 依赖: systemd-inhibit (systemd) 或 xset (X11)
# 用法: systemctl --user enable --now keep-awake.service
#       或直接运行: bash tools/keep-awake.sh
set -euo pipefail
INTERVAL=${INTERVAL:-300}

log() { echo "[$(date '+%F %T')] $*" >&2; }

while true; do
  if command -v systemd-inhibit >/dev/null 2>&1; then
    systemd-inhibit --what=idle:sleep:lock --why="contentkit 长任务保活" \
      sleep "${INTERVAL}" 2>/dev/null || log "inhibit 失败一次，继续"
  elif command -v xset >/dev/null 2>&1; then
    xset s off -dpms 2>/dev/null || log "xset 失败一次，继续"
  else
    log "无 systemd-inhibit/xset，保活不可用" >&2
    exit 1
  fi
  log "已抑制息屏/锁屏，下一轮 $INTERVAL 秒后"
  sleep "${INTERVAL}"
done
