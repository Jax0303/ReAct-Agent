"""
HITL (Human-in-the-Loop) 승인 에이전트
Human Approval Agent
"""
import logging
from typing import Dict

try:
    from ..workflows.state import FinancialAgentState
except ImportError:
    from src.workflows.state import FinancialAgentState

logger = logging.getLogger(__name__)


class HumanApprovalAgent:
    """사용자 승인을 받는 에이전트"""
    
    def __init__(self):
        self.name = "HumanApprovalAgent"
    
    def approval_node(self, state: FinancialAgentState) -> FinancialAgentState:
        """
        사용자 승인을 요청하는 노드
        
        Args:
            state: 현재 워크플로우 상태
            
        Returns:
            업데이트된 상태 (승인/거부)
        """
        logger.info({
            "agent": "HumanApprovalAgent",
            "action": "approval_node",
            "status": "waiting_for_approval"
        })
        
        messages = state.get("messages", [])
        analysis = state.get("analysis", "")
        recommendations = state.get("recommendations", [])
        
        # 승인 요청 정보 로깅
        logger.info({
            "agent": "HumanApprovalAgent",
            "approval_request": {
                "analysis_length": len(analysis),
                "recommendations_count": len(recommendations),
                "current_status": state.get("status", "")
            }
        })
        
        # 환경 변수로 자동 승인 모드 체크
        import os
        auto_approve = os.getenv("AUTO_APPROVE", "false").lower() == "true"
        
        if auto_approve:
            logger.info({
                "agent": "HumanApprovalAgent",
                "action": "auto_approved",
                "reason": "AUTO_APPROVE environment variable is set"
            })
            
            messages.append({
                "role": "system",
                "content": "자동 승인 모드: 분석 결과가 자동으로 승인되었습니다."
            })
        else:
            # 실제 사용자 승인 요청
            logger.info({
                "agent": "HumanApprovalAgent",
                "message": "사용자 승인을 기다리는 중...",
                "prompt": "계속 진행하시겠습니까?"
            })
            
            # 콘솔 출력
            print("\n" + "="*60)
            print("🔔 사용자 승인 필요 (HITL - Human-in-the-Loop)")
            print("="*60)
            print(f"\n📊 분석 요약:")
            print(f"   - 주식: {state.get('stock_symbol', 'N/A')}")
            print(f"   - 분석 길이: {len(analysis)} 자")
            print(f"   - 추천사항: {len(recommendations)}개")
            
            if analysis:
                print(f"\n📝 분석 미리보기:")
                print(f"   {analysis[:200]}...")
            
            if recommendations:
                print(f"\n💡 추천사항 미리보기:")
                for i, rec in enumerate(recommendations[:3], 1):
                    print(f"   {i}. {rec}")
            
            print("\n" + "-"*60)
            
            try:
                approval = input("\n✅ 계속 진행하시겠습니까? (y/n): ").strip().lower()
            except EOFError:
                # 비대화형 환경에서는 자동 승인
                approval = 'y'
                logger.warning({
                    "agent": "HumanApprovalAgent",
                    "warning": "비대화형 환경 감지, 자동 승인"
                })
            
            if approval == 'y':
                logger.info({
                    "agent": "HumanApprovalAgent",
                    "action": "approved",
                    "user_decision": "yes"
                })
                
                messages.append({
                    "role": "system",
                    "content": "사용자가 분석 결과를 승인했습니다."
                })
            else:
                logger.warning({
                    "agent": "HumanApprovalAgent",
                    "action": "rejected",
                    "user_decision": "no"
                })
                
                state["status"] = "cancelled"
                state["errors"].append("사용자가 승인하지 않음")
                messages.append({
                    "role": "system",
                    "content": "사용자가 분석 결과를 거부했습니다. 워크플로우를 중단합니다."
                })
                
                # 거부 시 빈 최종 보고서
                state["final_report"] = "사용자 승인 거부로 인해 보고서 생성이 취소되었습니다."
        
        state["messages"] = messages
        
        logger.info({
            "agent": "HumanApprovalAgent",
            "status": "completed",
            "final_status": state.get("status", "")
        })
        
        return state

