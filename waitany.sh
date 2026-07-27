#!/bin/bash
cd /home/claude/icfpc2026
declare -A T=( [pathfinder]=4877A1BEFADA865493CBC66EE2DD5762 [subset-sum]=BC35C3BA6484D9E73ACF9BF5A5A128AF [little-little-man]=06112FCD798C808C2C15024B2C49A1CA [lllm-fix]=E6CA81F27C38ED1304A1D1F06EC29F11 )
for i in $(seq 1 "${2:-9}"); do
  for n in "${!T[@]}"; do
    g=$(timeout 60 node cdp.js eval "${T[$n]}" "(()=>!!document.querySelector('[data-testid=\"stop-button\"]'))()" 2>/dev/null | tail -1)
    if [ "$g" = "false" ]; then echo "IDLE:$n"; fi
  done
  sleep_done=$(python3 -c "import time; time.sleep(${1:-55}); print('x')")
done
echo "---tick done---"
