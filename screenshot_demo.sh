#!/bin/bash

echo "=========================================="
echo "📸 스크린샷 1: 전체 워크플로우 실행"
echo "=========================================="
export PYTHONPATH=/home/user/ReAct-Agent:$PYTHONPATH
export AUTO_APPROVE=true
python3 src/main.py AAPL 2>&1 | grep -v "^E0000\|^W0000\|^I0000\|^2025-" | tail -60

echo ""
echo ""
echo "=========================================="
echo "📸 스크린샷 2: 구조적 로깅 + HITL"
echo "=========================================="
python3 src/main.py TSLA 2>&1 | grep -E "agent.*Research|action.*collected|normalizer|HumanApproval|auto_approved" | head -20

echo ""
echo ""
echo "=========================================="
echo "📸 스크린샷 3: 스트리밍 모드"
echo "=========================================="
timeout 60 python3 src/main.py MSFT stream 2>&1 | grep -E "^(🔍|📊|💡|✋|📝|✅)"
