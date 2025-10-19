"""
금융 관련 에이전트들
Financial Agents
"""
import json
import logging
from typing import Dict, Any
from openai import OpenAI
import os

from ..workflows.state import FinancialAgentState
from ..tools.stock_tools import StockDataTool, FinancialNewsTool
from ..tools.calculator_tool import CalculatorTool

logger = logging.getLogger(__name__)


class FinancialAgent:
    """기본 금융 에이전트"""
    
    def __init__(self, openai_api_key: str, tavily_api_key: str = None):
        self.client = OpenAI(api_key=openai_api_key)
        self.stock_tool = StockDataTool()
        self.news_tool = FinancialNewsTool(tavily_api_key)
        self.calculator_tool = CalculatorTool()
    
    def _call_llm(self, messages: list, temperature: float = 0.1) -> str:
        """LLM 호출"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=temperature,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM 호출 실패: {str(e)}")
            return f"LLM 호출 중 오류가 발생했습니다: {str(e)}"


class ResearchAgent(FinancialAgent):
    """데이터 수집 전문 에이전트"""
    
    def __init__(self, openai_api_key: str, tavily_api_key: str = None):
        super().__init__(openai_api_key, tavily_api_key)
    
    def research_node(self, state: FinancialAgentState) -> FinancialAgentState:
        """연구 단계 - 주식 데이터와 뉴스 수집"""
        logger.info({
            "agent": "ResearchAgent",
            "action": "research_node",
            "stock_symbol": state.get("stock_symbol", ""),
            "status": "starting"
        })
        
        stock_symbol = state.get("stock_symbol", "")
        messages = state.get("messages", [])
        errors = state.get("errors", [])
        tool_history = state.get("tool_history", [])
        
        # 메시지 추가
        messages.append({
            "role": "system",
            "content": f"주식 {stock_symbol}에 대한 데이터 수집을 시작합니다."
        })
        
        # 주식 데이터 수집
        stock_result = self.stock_tool.run(stock_symbol)
        tool_history.append({
            "tool": "stock_data_tool",
            "input": {"symbol": stock_symbol},
            "output": stock_result
        })
        
        if stock_result.get("status") == "success":
            state["stock_data"] = stock_result
            messages.append({
                "role": "assistant",
                "content": f"주식 데이터 수집 완료: {stock_symbol}의 현재 가격은 ${stock_result.get('current_price', 'N/A')}입니다."
            })
        else:
            error_msg = f"주식 데이터 수집 실패: {stock_result.get('error', 'Unknown error')}"
            errors.append(error_msg)
            messages.append({
                "role": "assistant",
                "content": error_msg
            })
        
        # 뉴스 데이터 수집
        news_query = f"{stock_symbol} stock news"
        news_result = self.news_tool.run(news_query, max_results=3)
        tool_history.append({
            "tool": "financial_news_tool",
            "input": {"query": news_query, "max_results": 3},
            "output": news_result
        })
        
        if news_result.get("status") == "success":
            state["news_data"] = news_result.get("results", [])
            messages.append({
                "role": "assistant",
                "content": f"{len(news_result.get('results', []))}개의 관련 뉴스를 찾았습니다."
            })
        else:
            error_msg = f"뉴스 수집 실패: {news_result.get('error', 'Unknown error')}"
            errors.append(error_msg)
            messages.append({
                "role": "assistant",
                "content": error_msg
            })
        
        # 상태 업데이트
        state.update({
            "messages": messages,
            "errors": errors,
            "tool_history": tool_history,
            "status": "analyzing"
        })
        
        logger.info({
            "agent": "ResearchAgent",
            "status": "completed",
            "stock_data_collected": stock_result.get("status") == "success",
            "news_collected": news_result.get("status") == "success"
        })
        
        return state


class AnalysisAgent(FinancialAgent):
    """분석 전문 에이전트"""
    
    def __init__(self, openai_api_key: str, tavily_api_key: str = None):
        super().__init__(openai_api_key, tavily_api_key)
    
    def analyze_node(self, state: FinancialAgentState) -> FinancialAgentState:
        """분석 단계 - 수집된 데이터 분석"""
        logger.info({
            "agent": "AnalysisAgent",
            "action": "analyze_node",
            "status": "starting"
        })
        
        stock_data = state.get("stock_data")
        news_data = state.get("news_data", [])
        messages = state.get("messages", [])
        
        # 분석 프롬프트 생성
        analysis_prompt = self._create_analysis_prompt(stock_data, news_data, state.get("user_query", ""))
        
        llm_messages = [
            {"role": "system", "content": "당신은 전문적인 주식 분석가입니다. 주어진 데이터를 바탕으로 객관적이고 전문적인 분석을 제공하세요."},
            {"role": "user", "content": analysis_prompt}
        ]
        
        # LLM으로 분석 수행
        analysis_result = self._call_llm(llm_messages)
        
        state["analysis"] = analysis_result
        messages.append({
            "role": "assistant",
            "content": f"분석 완료: {analysis_result[:200]}..."
        })
        
        state.update({
            "messages": messages,
            "status": "recommending"
        })
        
        logger.info({
            "agent": "AnalysisAgent",
            "status": "completed"
        })
        
        return state
    
    def _create_analysis_prompt(self, stock_data: Dict, news_data: list, user_query: str) -> str:
        """분석을 위한 프롬프트 생성"""
        prompt = f"""
사용자 질문: {user_query}

주식 데이터:
{json.dumps(stock_data, indent=2, ensure_ascii=False) if stock_data else "주식 데이터를 가져올 수 없었습니다."}

뉴스 데이터:
{json.dumps(news_data, indent=2, ensure_ascii=False) if news_data else "뉴스 데이터를 가져올 수 없었습니다."}

위 데이터를 바탕으로 다음을 분석해주세요:
1. 현재 주가 상황과 트렌드
2. 주요 지표 분석 (PER, 거래량, 52주 고저점 등)
3. 최신 뉴스의 영향 분석
4. 기술적/기본적 분석 결론

분석은 객관적이고 전문적으로 작성해주세요.
"""
        return prompt


class RecommendationAgent(FinancialAgent):
    """추천 전문 에이전트"""
    
    def __init__(self, openai_api_key: str, tavily_api_key: str = None):
        super().__init__(openai_api_key, tavily_api_key)
    
    def recommend_node(self, state: FinancialAgentState) -> FinancialAgentState:
        """추천 단계 - 투자 추천사항 생성"""
        logger.info({
            "agent": "RecommendationAgent",
            "action": "recommend_node",
            "status": "starting"
        })
        
        analysis = state.get("analysis", "")
        stock_data = state.get("stock_data")
        messages = state.get("messages", [])
        tool_history = state.get("tool_history", [])
        
        # 계산이 필요한 경우 계산기 도구 사용
        if stock_data and stock_data.get("current_price") != "N/A":
            current_price = stock_data.get("current_price")
            pe_ratio = stock_data.get("pe_ratio")
            
            if pe_ratio != "N/A" and pe_ratio:
                # 예시: PER 기반 가치 평가 계산
                calc_expression = f"{current_price} / {pe_ratio}"
                calc_result = self.calculator_tool.run(calc_expression)
                tool_history.append({
                    "tool": "calculator_tool",
                    "input": {"expression": calc_expression},
                    "output": calc_result
                })
        
        # 추천 프롬프트 생성
        recommendation_prompt = self._create_recommendation_prompt(analysis, stock_data)
        
        llm_messages = [
            {"role": "system", "content": "당신은 신중하고 책임감 있는 투자 자문가입니다. 리스크와 보수를 균형있게 고려한 추천을 제공하세요. 모든 추천은 면책조항과 함께 제공하세요."},
            {"role": "user", "content": recommendation_prompt}
        ]
        
        # LLM으로 추천 생성
        recommendation_result = self._call_llm(llm_messages)
        
        # 추천사항을 리스트로 파싱
        recommendations = self._parse_recommendations(recommendation_result)
        
        state["recommendations"] = recommendations
        messages.append({
            "role": "assistant",
            "content": f"추천사항 생성 완료: {len(recommendations)}개의 추천사항을 제공합니다."
        })
        
        state.update({
            "messages": messages,
            "tool_history": tool_history,
            "status": "reviewing"
        })
        
        logger.info({
            "agent": "RecommendationAgent",
            "status": "completed",
            "recommendations_count": len(recommendations)
        })
        
        return state
    
    def _create_recommendation_prompt(self, analysis: str, stock_data: Dict) -> str:
        """추천을 위한 프롬프트 생성"""
        prompt = f"""
다음 분석 결과를 바탕으로 투자 추천사항을 제공해주세요:

분석 결과:
{analysis}

주식 데이터:
{json.dumps(stock_data, indent=2, ensure_ascii=False) if stock_data else "주식 데이터 없음"}

다음 형식으로 추천사항을 작성해주세요:
1. [매수/매도/보유] - 간단한 추천
2. 목표가치: $XX (근거)
3. 리스크: 주요 리스크 요소들
4. 추천 이유: 핵심 근거 3가지
5. 주의사항: 투자 시 주의할 점

면책조항: 이 추천은 참고용이며, 투자 결정은 개인 책임입니다.
"""
        return prompt
    
    def _parse_recommendations(self, recommendation_text: str) -> list:
        """추천 텍스트를 리스트로 파싱"""
        lines = recommendation_text.split('\n')
        recommendations = []
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith(('1.', '2.', '3.', '4.', '5.')) or 
                        line.startswith(('-', '*', '•'))):
                recommendations.append(line)
        
        return recommendations if recommendations else [recommendation_text]


class ReviewAgent(FinancialAgent):
    """검토 및 최종 보고서 생성 에이전트"""
    
    def __init__(self, openai_api_key: str, tavily_api_key: str = None):
        super().__init__(openai_api_key, tavily_api_key)
    
    def review_node(self, state: FinancialAgentState) -> FinancialAgentState:
        """검토 단계 - 최종 보고서 생성"""
        logger.info({
            "agent": "ReviewAgent",
            "action": "review_node",
            "status": "starting"
        })
        
        user_query = state.get("user_query", "")
        stock_data = state.get("stock_data")
        analysis = state.get("analysis", "")
        recommendations = state.get("recommendations", [])
        messages = state.get("messages", [])
        
        # 최종 보고서 프롬프트 생성
        report_prompt = self._create_report_prompt(
            user_query, stock_data, analysis, recommendations
        )
        
        llm_messages = [
            {"role": "system", "content": "당신은 전문 금융 분석가입니다. 수집된 모든 정보를 종합하여 명확하고 완전한 투자 보고서를 작성하세요."},
            {"role": "user", "content": report_prompt}
        ]
        
        # LLM으로 최종 보고서 생성
        final_report = self._call_llm(llm_messages)
        
        state["final_report"] = final_report
        messages.append({
            "role": "assistant",
            "content": "최종 보고서가 완성되었습니다."
        })
        
        state.update({
            "messages": messages,
            "status": "done"
        })
        
        logger.info({
            "agent": "ReviewAgent",
            "status": "completed"
        })
        
        return state
    
    def _create_report_prompt(self, user_query: str, stock_data: Dict, 
                            analysis: str, recommendations: list) -> str:
        """최종 보고서를 위한 프롬프트 생성"""
        prompt = f"""
사용자 질문: {user_query}

모든 분석 결과를 종합하여 전문적인 투자 보고서를 작성해주세요:

주식 데이터:
{json.dumps(stock_data, indent=2, ensure_ascii=False) if stock_data else "주식 데이터 없음"}

분석 결과:
{analysis}

추천사항:
{json.dumps(recommendations, indent=2, ensure_ascii=False)}

다음 구조로 보고서를 작성해주세요:
1. 요약 (Executive Summary)
2. 주식 개요 및 현재 상황
3. 핵심 분석 내용
4. 투자 추천사항
5. 리스크 및 주의사항
6. 결론

보고서는 전문적이고 이해하기 쉽게 작성되어야 합니다.
"""
        return prompt
