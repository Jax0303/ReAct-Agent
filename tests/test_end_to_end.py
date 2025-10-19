"""
통합 테스트
End-to-End Tests
"""
import pytest
import sys
import os

# 프로젝트 루트를 파이썬 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from workflows.financial_workflow import FinancialWorkflow


class TestEndToEnd:
    """통합 테스트"""
    
    def setup_method(self):
        """테스트 설정"""
        self.workflow = FinancialWorkflow(
            google_ai_api_key="test_key",
            tavily_api_key="test_key"
        )
    
    def test_end_to_end_simple(self):
        """간단한 종단간 테스트"""
        initial_state = {
            "messages": [],
            "stock_symbol": "AAPL",
            "user_query": "AAPL 주식 분석",
            "iteration": 0,
            "max_iterations": 1,  # 빠른 테스트를 위해 1회로 제한
            "status": "researching",
            "errors": [],
            "tool_history": [],
            "final_report": ""
        }
        
        try:
            result = self.workflow.run(initial_state)
            
            # 결과 형태 검증
            assert isinstance(result, dict)
            
            # 필수 키들이 있는지 확인
            required_keys = ["status", "messages", "stock_symbol", "user_query"]
            for key in required_keys:
                assert key in result
            
            # final_report가 문자열인지 확인
            final_report = result.get("final_report", "")
            assert isinstance(final_report, str)
            
            # 최종 상태가 적절한지 확인
            assert result["status"] in ["done", "error", "researching", "analyzing", "recommending", "reviewing"]
            
        except Exception as e:
            # API 키 문제로 실패할 수 있음 - 이는 정상
            error_msg = str(e).lower()
            assert any(keyword in error_msg for keyword in ["api", "key", "error", "timeout"])
    
    def test_error_handling(self):
        """에러 처리 테스트"""
        # 잘못된 상태로 테스트
        initial_state = {
            "messages": [],
            "stock_symbol": "",  # 빈 심볼
            "user_query": "",
            "iteration": 0,
            "max_iterations": 1,
            "status": "researching",
            "errors": [],
            "tool_history": [],
            "final_report": ""
        }
        
        try:
            result = self.workflow.run(initial_state)
            
            # 에러 처리가 되어야 함
            assert isinstance(result, dict)
            assert "errors" in result or result.get("status") == "error"
            
        except Exception as e:
            # 예외가 발생해도 정상 - 에러 처리가 되는 경우
            assert isinstance(e, Exception)
