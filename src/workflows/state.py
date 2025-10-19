"""
금융 ReAct 에이전트를 위한 State 정의
Financial ReAct Agent State Definition
"""
from typing import TypedDict, Annotated, List, Dict, Optional
import operator


class FinancialAgentState(TypedDict):
    """금융 에이전트의 상태를 관리하는 TypedDict"""
    
    # 로그/대화 누적
    messages: Annotated[List[Dict[str, str]], operator.add]
    
    # 현재 분석할 주식 심볼
    stock_symbol: str
    
    # 초기 질문/요청
    user_query: str
    
    # 데이터 수집 단계의 결과들
    stock_data: Optional[Dict]
    market_data: Optional[Dict]
    news_data: Optional[List[Dict]]
    
    # 분석 결과
    analysis: Optional[str]
    
    # 추천사항
    recommendations: Optional[List[str]]
    
    # 최종 보고서
    final_report: str
    
    # 반복 제어
    iteration: int
    max_iterations: int
    
    # 현재 상태
    status: str  # researching/analyzing/recommending/reviewing/done
    
    # 에러 상태
    errors: Annotated[List[str], operator.add]
    
    # 도구 사용 히스토리
    tool_history: Annotated[List[Dict], operator.add]
