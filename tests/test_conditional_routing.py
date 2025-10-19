"""
조건부 라우팅 테스트
Tests for Conditional Routing
"""
import pytest
import os
import sys

# 경로 설정
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from workflows.financial_workflow import FinancialWorkflow
from workflows.state import FinancialAgentState


class TestConditionalRouting:
    """조건부 라우팅 테스트"""
    
    def test_approval_routing_approved(self):
        """
        승인 라우팅 테스트 - 승인됨
        """
        # 더미 API 키로 워크플로우 생성
        workflow = FinancialWorkflow(
            google_ai_api_key=os.getenv("GOOGLE_AI_API_KEY", "dummy_key"),
            tavily_api_key=os.getenv("TAVILY_API_KEY")
        )
        
        # 승인된 상태
        state = FinancialAgentState({
            "messages": [],
            "stock_symbol": "AAPL",
            "user_query": "Analyze AAPL",
            "iteration": 0,
            "max_iterations": 3,
            "status": "approved",  # 승인됨
            "errors": [],
            "tool_history": [],
            "stock_data": {},
            "market_data": {},
            "news_data": [],
            "analysis": "Test analysis",
            "recommendations": ["Test recommendation"],
            "final_report": ""
        })
        
        # 승인 체크 함수 테스트
        result = workflow._check_approval_status(state)
        
        assert result == "approved", "Should route to 'approved' path"
        
        print(f"✅ 승인 라우팅 테스트 통과: {result}")
    
    def test_approval_routing_rejected(self):
        """
        승인 라우팅 테스트 - 거부됨
        """
        workflow = FinancialWorkflow(
            google_ai_api_key=os.getenv("GOOGLE_AI_API_KEY", "dummy_key"),
            tavily_api_key=os.getenv("TAVILY_API_KEY")
        )
        
        # 거부된 상태
        state = FinancialAgentState({
            "messages": [],
            "stock_symbol": "AAPL",
            "user_query": "Analyze AAPL",
            "iteration": 0,
            "max_iterations": 3,
            "status": "cancelled",  # 취소됨 (거부)
            "errors": ["User rejected"],
            "tool_history": [],
            "stock_data": {},
            "market_data": {},
            "news_data": [],
            "analysis": "Test analysis",
            "recommendations": ["Test recommendation"],
            "final_report": ""
        })
        
        # 승인 체크 함수 테스트
        result = workflow._check_approval_status(state)
        
        assert result == "rejected", "Should route to 'rejected' path"
        
        print(f"✅ 거부 라우팅 테스트 통과: {result}")
    
    def test_continue_routing_max_iterations(self):
        """
        계속 진행 라우팅 테스트 - 최대 반복 도달
        """
        workflow = FinancialWorkflow(
            google_ai_api_key=os.getenv("GOOGLE_AI_API_KEY", "dummy_key"),
            tavily_api_key=os.getenv("TAVILY_API_KEY")
        )
        
        # 최대 반복 도달 상태
        state = FinancialAgentState({
            "messages": [],
            "stock_symbol": "AAPL",
            "user_query": "Analyze AAPL",
            "iteration": 3,  # 최대값
            "max_iterations": 3,
            "status": "researching",
            "errors": [],
            "tool_history": [],
            "stock_data": {},
            "market_data": {},
            "news_data": [],
            "analysis": "",
            "recommendations": [],
            "final_report": ""
        })
        
        # 계속 진행 체크 함수 테스트
        result = workflow._should_continue(state)
        
        assert result == "end", "Should route to 'end' when max iterations reached"
        
        print(f"✅ 최대 반복 라우팅 테스트 통과: {result}")
    
    def test_continue_routing_critical_errors(self):
        """
        계속 진행 라우팅 테스트 - 치명적 오류 발생
        """
        workflow = FinancialWorkflow(
            google_ai_api_key=os.getenv("GOOGLE_AI_API_KEY", "dummy_key"),
            tavily_api_key=os.getenv("TAVILY_API_KEY")
        )
        
        # 치명적 오류가 있는 상태
        state = FinancialAgentState({
            "messages": [],
            "stock_symbol": "AAPL",
            "user_query": "Analyze AAPL",
            "iteration": 1,
            "max_iterations": 3,
            "status": "researching",
            "errors": [
                "API connection timeout",  # 치명적 오류
                "Network error occurred"   # 치명적 오류
            ],
            "tool_history": [],
            "stock_data": {},
            "market_data": {},
            "news_data": [],
            "analysis": "",
            "recommendations": [],
            "final_report": ""
        })
        
        # 계속 진행 체크 함수 테스트
        result = workflow._should_continue(state)
        
        assert result == "end", "Should route to 'end' when critical errors exist"
        
        print(f"✅ 치명적 오류 라우팅 테스트 통과: {result}")
    
    def test_continue_routing_missing_data(self):
        """
        계속 진행 라우팅 테스트 - 데이터 누락 시 재시도
        """
        workflow = FinancialWorkflow(
            google_ai_api_key=os.getenv("GOOGLE_AI_API_KEY", "dummy_key"),
            tavily_api_key=os.getenv("TAVILY_API_KEY")
        )
        
        # 데이터가 누락된 상태
        state = FinancialAgentState({
            "messages": [],
            "stock_symbol": "AAPL",
            "user_query": "Analyze AAPL",
            "iteration": 1,
            "max_iterations": 3,
            "status": "needs_more_data",
            "errors": [],
            "tool_history": [],
            "stock_data": None,  # 데이터 누락
            "market_data": {},
            "news_data": [],
            "analysis": "",
            "recommendations": [],
            "final_report": ""
        })
        
        # 계속 진행 체크 함수 테스트
        result = workflow._should_continue(state)
        
        assert result == "continue", "Should route to 'continue' when data is missing"
        
        print(f"✅ 데이터 누락 재시도 라우팅 테스트 통과: {result}")
    
    def test_continue_routing_normal_completion(self):
        """
        계속 진행 라우팅 테스트 - 정상 완료
        """
        workflow = FinancialWorkflow(
            google_ai_api_key=os.getenv("GOOGLE_AI_API_KEY", "dummy_key"),
            tavily_api_key=os.getenv("TAVILY_API_KEY")
        )
        
        # 정상 완료 상태
        state = FinancialAgentState({
            "messages": [],
            "stock_symbol": "AAPL",
            "user_query": "Analyze AAPL",
            "iteration": 1,
            "max_iterations": 3,
            "status": "completed",
            "errors": [],
            "tool_history": [],
            "stock_data": {"status": "success"},
            "market_data": {},
            "news_data": [{"title": "News 1"}],
            "analysis": "Complete analysis",
            "recommendations": ["Recommendation 1"],
            "final_report": "Final report"
        })
        
        # 계속 진행 체크 함수 테스트
        result = workflow._should_continue(state)
        
        assert result == "end", "Should route to 'end' on normal completion"
        
        print(f"✅ 정상 완료 라우팅 테스트 통과: {result}")
    
    def test_multiple_routing_decisions(self):
        """
        여러 라우팅 결정 테스트
        """
        workflow = FinancialWorkflow(
            google_ai_api_key=os.getenv("GOOGLE_AI_API_KEY", "dummy_key"),
            tavily_api_key=os.getenv("TAVILY_API_KEY")
        )
        
        test_cases = [
            {
                "name": "승인 경로",
                "state": {"status": "approved"},
                "function": "_check_approval_status",
                "expected": "approved"
            },
            {
                "name": "거부 경로",
                "state": {"status": "cancelled"},
                "function": "_check_approval_status",
                "expected": "rejected"
            },
            {
                "name": "반복 완료",
                "state": {"iteration": 3, "max_iterations": 3, "status": "completed", "errors": [], "stock_data": {}},
                "function": "_should_continue",
                "expected": "end"
            },
            {
                "name": "재시도 필요",
                "state": {"iteration": 1, "max_iterations": 3, "status": "needs_more_data", "errors": [], "stock_data": None},
                "function": "_should_continue",
                "expected": "continue"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            # 기본 상태 생성
            base_state = FinancialAgentState({
                "messages": [],
                "stock_symbol": "AAPL",
                "user_query": "Test",
                "iteration": 0,
                "max_iterations": 3,
                "status": "researching",
                "errors": [],
                "tool_history": [],
                "stock_data": {},
                "market_data": {},
                "news_data": [],
                "analysis": "",
                "recommendations": [],
                "final_report": ""
            })
            
            # 테스트 케이스별 상태 업데이트
            base_state.update(test_case["state"])
            
            # 함수 호출
            if test_case["function"] == "_check_approval_status":
                result = workflow._check_approval_status(base_state)
            else:
                result = workflow._should_continue(base_state)
            
            # 검증
            assert result == test_case["expected"], \
                f"Test case '{test_case['name']}' failed: expected {test_case['expected']}, got {result}"
            
            print(f"✅ 라우팅 결정 테스트 {i} 통과: {test_case['name']} -> {result}")
        
        print(f"✅ 여러 라우팅 결정 테스트 통과 (총 {len(test_cases)}개)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

