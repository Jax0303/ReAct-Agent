"""
금융 ReAct 에이전트 워크플로우
Financial ReAct Agent Workflow
"""
import logging
from typing import Dict, Any
from langgraph.graph import StateGraph, END

try:
    from .state import FinancialAgentState
    from ..agents.financial_agents import ResearchAgent, AnalysisAgent, RecommendationAgent, ReviewAgent
except ImportError:
    # 테스트 환경에서 절대 import 사용
    from src.workflows.state import FinancialAgentState
    from src.agents.financial_agents import ResearchAgent, AnalysisAgent, RecommendationAgent, ReviewAgent

logger = logging.getLogger(__name__)


class FinancialWorkflow:
    """금융 ReAct 에이전트 워크플로우"""
    
    def __init__(self, google_ai_api_key: str, tavily_api_key: str = None):
        self.google_ai_api_key = google_ai_api_key
        self.tavily_api_key = tavily_api_key
        
        # 에이전트 초기화
        self.research_agent = ResearchAgent(google_ai_api_key, tavily_api_key)
        self.analysis_agent = AnalysisAgent(google_ai_api_key, tavily_api_key)
        self.recommendation_agent = RecommendationAgent(google_ai_api_key, tavily_api_key)
        self.review_agent = ReviewAgent(google_ai_api_key, tavily_api_key)
        
        # 워크플로우 빌드
        self.app = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """워크플로우 빌드"""
        workflow = StateGraph(FinancialAgentState)
        
        # 노드 추가
        workflow.add_node("research", self.research_agent.research_node)
        workflow.add_node("analyze", self.analysis_agent.analyze_node)
        workflow.add_node("recommend", self.recommendation_agent.recommend_node)
        workflow.add_node("review", self.review_agent.review_node)
        
        # 엔트리 포인트 설정
        workflow.set_entry_point("research")
        
        # 순차적 엣지 추가
        workflow.add_edge("research", "analyze")
        workflow.add_edge("analyze", "recommend")
        workflow.add_edge("recommend", "review")
        
        # 조건부 엣지 추가 (재시도 로직)
        workflow.add_conditional_edges(
            "review",
            self._should_continue,
            {
                "continue": "research",  # 재시도
                "end": END
            }
        )
        
        return workflow.compile()
    
    def _should_continue(self, state: FinancialAgentState) -> str:
        """계속 진행할지 결정하는 함수"""
        iteration = state.get("iteration", 0)
        max_iterations = state.get("max_iterations", 3)
        status = state.get("status", "")
        errors = state.get("errors", [])
        
        # 최대 반복 횟수 체크
        if iteration >= max_iterations:
            logger.info({
                "decision": "should_continue",
                "result": "end",
                "reason": "max_iterations_reached",
                "iteration": iteration,
                "max_iterations": max_iterations
            })
            return "end"
        
        # 심각한 에러가 있는지 체크
        critical_errors = [
            error for error in errors 
            if any(keyword in error.lower() for keyword in ["api", "network", "timeout", "critical"])
        ]
        
        if critical_errors and len(critical_errors) >= 2:
            logger.info({
                "decision": "should_continue",
                "result": "end",
                "reason": "critical_errors",
                "error_count": len(critical_errors)
            })
            return "end"
        
        # 상태가 done이면 종료
        if status == "done":
            logger.info({
                "decision": "should_continue",
                "result": "end",
                "reason": "status_done"
            })
            return "end"
        
        # 데이터가 부족하면 재시도
        stock_data = state.get("stock_data")
        news_data = state.get("news_data", [])
        
        if not stock_data or stock_data.get("status") != "success":
            if iteration < max_iterations - 1:
                logger.info({
                    "decision": "should_continue",
                    "result": "continue",
                    "reason": "missing_stock_data",
                    "iteration": iteration
                })
                return "continue"
        
        logger.info({
            "decision": "should_continue",
            "result": "end",
            "reason": "normal_completion",
            "status": status
        })
        return "end"
    
    def run(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """워크플로우 실행"""
        logger.info({
            "workflow": "FinancialWorkflow",
            "action": "run",
            "stock_symbol": initial_state.get("stock_symbol"),
            "status": "starting"
        })
        
        try:
            # 초기 상태 설정
            state = FinancialAgentState({
                "messages": initial_state.get("messages", []),
                "stock_symbol": initial_state.get("stock_symbol", ""),
                "user_query": initial_state.get("user_query", ""),
                "iteration": initial_state.get("iteration", 0),
                "max_iterations": initial_state.get("max_iterations", 3),
                "status": initial_state.get("status", "researching"),
                "errors": initial_state.get("errors", []),
                "tool_history": initial_state.get("tool_history", []),
                "stock_data": initial_state.get("stock_data"),
                "market_data": initial_state.get("market_data"),
                "news_data": initial_state.get("news_data", []),
                "analysis": initial_state.get("analysis"),
                "recommendations": initial_state.get("recommendations"),
                "final_report": initial_state.get("final_report", "")
            })
            
            # 워크플로우 실행
            result = self.app.invoke(state)
            
            logger.info({
                "workflow": "FinancialWorkflow",
                "status": "completed",
                "final_status": result.get("status"),
                "final_report_length": len(result.get("final_report", ""))
            })
            
            return result
            
        except Exception as e:
            logger.error({
                "workflow": "FinancialWorkflow",
                "status": "error",
                "error": str(e)
            })
            
            # 에러 상태 반환
            return {
                **initial_state,
                "status": "error",
                "errors": initial_state.get("errors", []) + [f"워크플로우 실행 오류: {str(e)}"],
                "final_report": "죄송합니다. 워크플로우 실행 중 오류가 발생했습니다."
            }
