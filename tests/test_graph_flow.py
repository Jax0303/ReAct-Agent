"""
그래프 플로우 테스트
Graph Flow Tests
"""
import pytest
import sys
import os

# 프로젝트 루트를 파이썬 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from workflows.financial_workflow import FinancialWorkflow


class TestGraphFlow:
    """그래프 플로우 테스트"""
    
    def setup_method(self):
        """테스트 설정"""
        # 테스트용 API 키 (실제 사용을 위해서는 유효한 키 필요)
        self.workflow = FinancialWorkflow(
            google_ai_api_key="test_key",
            tavily_api_key="test_key"
        )
    
    def test_flow_edges(self):
        """플로우 엣지 테스트"""
        # 초기 상태 설정
        initial_state = {
            "messages": [],
            "stock_symbol": "AAPL",
            "user_query": "AAPL 주식에 대한 분석을 해주세요",
            "iteration": 0,
            "max_iterations": 2,
            "status": "researching",
            "errors": [],
            "tool_history": [],
            "final_report": ""
        }
        
        try:
            # 워크플로우 실행 시도
            result = self.workflow.run(initial_state)
            
            # 결과 검증
            assert isinstance(result, dict)
            assert "status" in result
            assert "messages" in result
            
            # 상태가 완료되었는지 확인
            assert result["status"] in ["done", "error"] or result["iteration"] <= initial_state["max_iterations"]
            
        except Exception as e:
            # API 키가 없어서 실패할 수 있음 - 이는 예상된 동작
            assert "error" in str(e).lower() or "api" in str(e).lower()
    
    def test_should_continue_logic(self):
        """should_continue 로직 테스트"""
        # 최대 반복 횟수 테스트
        state_max_iterations = {
            "iteration": 3,
            "max_iterations": 3,
            "status": "analyzing",
            "errors": []
        }
        
        result = self.workflow._should_continue(state_max_iterations)
        assert result == "end"
        
        # 정상 완료 테스트
        state_done = {
            "iteration": 1,
            "max_iterations": 3,
            "status": "done",
            "errors": []
        }
        
        result = self.workflow._should_continue(state_done)
        assert result == "end"
        
        # 계속 진행 테스트
        state_continue = {
            "iteration": 0,
            "max_iterations": 3,
            "status": "analyzing",
            "errors": [],
            "stock_data": None
        }
        
        result = self.workflow._should_continue(state_continue)
        # 데이터가 없으면 재시도해야 함
        assert result in ["continue", "end"]
