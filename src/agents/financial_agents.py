"""
금융 관련 에이전트들
Financial Agents
"""
import json
import logging
from typing import Dict, Any
import os
import google.generativeai as genai

try:
    from ..workflows.state import FinancialAgentState
    from ..tools.stock_tools import StockDataTool, FinancialNewsTool
    from ..tools.calculator_tool import CalculatorTool
except ImportError:
    # 테스트 환경에서 절대 import 사용
    from src.workflows.state import FinancialAgentState
    from src.tools.stock_tools import StockDataTool, FinancialNewsTool
    from src.tools.calculator_tool import CalculatorTool

logger = logging.getLogger(__name__)


class FinancialAgent:
    """기본 금융 에이전트"""
    
    def __init__(self, google_ai_api_key: str, tavily_api_key: str = None):
        # Google AI 설정
        genai.configure(api_key=google_ai_api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')  # Gemini 2.0 Flash (최신 모델)
        self.stock_tool = StockDataTool()
        self.news_tool = FinancialNewsTool(tavily_api_key)
        self.calculator_tool = CalculatorTool()
    
    def _call_llm(self, messages: list, temperature: float = 0.1) -> str:
        """LLM 호출 - Google Gemini 사용"""
        try:
            # Gemini API 형식으로 메시지 변환
            prompt_text = ""
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "system":
                    prompt_text += f"System: {content}\n\n"
                elif role == "user":
                    prompt_text += f"User: {content}\n\n"
                elif role == "assistant":
                    prompt_text += f"Assistant: {content}\n\n"
            
            # Google AI 생성 설정
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=1000,
                top_p=0.8,
                top_k=40
            )
            
            response = self.model.generate_content(
                prompt_text,
                generation_config=generation_config
            )
            
            return response.text
        except Exception as e:
            error_msg = str(e)
            logger.error(f"LLM 호출 실패: {error_msg}")
            
            # 할당량 초과 오류인 경우 특별 처리
            if "quota" in error_msg.lower() or "429" in error_msg or "quota" in error_msg.lower():
                return "API 할당량이 부족하여 LLM 분석을 수행할 수 없습니다. 주식 데이터와 뉴스 정보만으로 분석을 제공합니다."
            elif "rate limit" in error_msg.lower():
                return "API 호출 한도에 도달했습니다. 잠시 후 다시 시도해주세요."
            else:
                return f"LLM 호출 중 오류가 발생했습니다: {error_msg}"


class ResearchAgent(FinancialAgent):
    """데이터 수집 전문 에이전트"""
    
    def __init__(self, google_ai_api_key: str, tavily_api_key: str = None):
        super().__init__(google_ai_api_key, tavily_api_key)
    
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
    
    def __init__(self, google_ai_api_key: str, tavily_api_key: str = None):
        super().__init__(google_ai_api_key, tavily_api_key)
    
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
        
        # LLM 호출 실패시 기본 분석 제공
        if "API 할당량이 부족" in analysis_result or "LLM 호출 중 오류" in analysis_result:
            analysis_result = self._create_fallback_analysis(stock_data, news_data)
        
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
    
    def _create_fallback_analysis(self, stock_data: Dict, news_data: list) -> str:
        """LLM 호출 실패시 기본 분석 제공"""
        if not stock_data:
            return "주식 데이터를 가져올 수 없어 분석을 수행할 수 없습니다."
        
        analysis = "=== 기본 주식 분석 ===\n\n"
        
        # 기본 정보
        symbol = stock_data.get("symbol", "Unknown")
        current_price = stock_data.get("current_price", "N/A")
        change = stock_data.get("change", "N/A")
        change_percent = stock_data.get("change_percent", "N/A")
        volume = stock_data.get("volume", "N/A")
        
        analysis += f"주식 심볼: {symbol}\n"
        analysis += f"현재 가격: ${current_price}\n"
        
        if change != "N/A" and change_percent != "N/A":
            trend = "상승" if change > 0 else "하락"
            analysis += f"가격 변동: {trend} (${change}, {change_percent:.2%})\n"
        
        if volume != "N/A":
            analysis += f"거래량: {volume:,}\n"
        
        # PER 분석
        pe_ratio = stock_data.get("pe_ratio", "N/A")
        if pe_ratio != "N/A":
            analysis += f"PER: {pe_ratio}\n"
            if pe_ratio < 15:
                analysis += "- PER이 낮아 상대적으로 저평가된 것으로 보입니다.\n"
            elif pe_ratio > 25:
                analysis += "- PER이 높아 상대적으로 고평가된 것으로 보입니다.\n"
            else:
                analysis += "- PER이 적정 수준입니다.\n"
        
        # 52주 고저점 분석
        high_52w = stock_data.get("52w_high", "N/A")
        low_52w = stock_data.get("52w_low", "N/A")
        
        if high_52w != "N/A" and low_52w != "N/A" and current_price != "N/A":
            high_pct = ((current_price - low_52w) / low_52w) * 100
            low_pct = ((high_52w - current_price) / high_52w) * 100
            analysis += f"\n52주 고점: ${high_52w} (현재가 대비 {low_pct:.1f}% 하락 가능성)\n"
            analysis += f"52주 저점: ${low_52w} (현재가 대비 {high_pct:.1f}% 상승 여력)\n"
        
        # 뉴스 분석
        if news_data:
            analysis += f"\n최신 뉴스: {len(news_data)}건 발견\n"
            for i, news in enumerate(news_data[:3], 1):
                title = news.get("title", "제목 없음")[:100]
                analysis += f"{i}. {title}...\n"
        else:
            analysis += "\n최신 뉴스: 관련 뉴스를 찾을 수 없었습니다.\n"
        
        analysis += "\n※ 이 분석은 기본적인 데이터 기반 분석입니다. LLM 분석이 사용되지 않았으므로 참고용으로만 사용하세요."
        
        return analysis


class RecommendationAgent(FinancialAgent):
    """추천 전문 에이전트"""
    
    def __init__(self, google_ai_api_key: str, tavily_api_key: str = None):
        super().__init__(google_ai_api_key, tavily_api_key)
    
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
        
        # LLM 호출 실패시 기본 추천 제공
        if "API 할당량이 부족" in recommendation_result or "LLM 호출 중 오류" in recommendation_result:
            recommendations = self._create_fallback_recommendations(stock_data, analysis)
        else:
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
    
    def _create_fallback_recommendations(self, stock_data: Dict, analysis: str) -> list:
        """LLM 호출 실패시 기본 추천 제공"""
        recommendations = []
        
        if not stock_data:
            return ["데이터 부족으로 추천을 제공할 수 없습니다."]
        
        current_price = stock_data.get("current_price", "N/A")
        pe_ratio = stock_data.get("pe_ratio", "N/A")
        change = stock_data.get("change", "N/A")
        
        # 기본 추천사항 생성
        recommendations.append("1. 보유 - 추가 정보 분석 후 결정 권장")
        
        if current_price != "N/A" and pe_ratio != "N/A":
            if pe_ratio < 15:
                recommendations.append("2. 상대적 매수 - PER이 낮은 편임")
            elif pe_ratio > 25:
                recommendations.append("2. 상대적 매도 - PER이 높은 편임")
            else:
                recommendations.append("2. 적정가치 - PER이 적정 수준")
        
        if change != "N/A":
            if change > 0:
                recommendations.append("3. 상승 추세 - 긍정적 모멘텀")
            else:
                recommendations.append("3. 하락 추세 - 주의 깊은 관찰 필요")
        
        recommendations.append("4. 리스크: 시장 변동성, 기업 실적 변화, 경제 상황 변화")
        recommendations.append("5. 주의사항: 투자 결정은 개인 책임이며, 충분한 검토 후 진행하세요")
        recommendations.append("면책조항: 이 추천은 참고용이며, 실제 투자 손실에 대해 책임지지 않습니다.")
        
        return recommendations


class ReviewAgent(FinancialAgent):
    """검토 및 최종 보고서 생성 에이전트"""
    
    def __init__(self, google_ai_api_key: str, tavily_api_key: str = None):
        super().__init__(google_ai_api_key, tavily_api_key)
    
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
        
        # LLM 호출 실패시 기본 보고서 생성
        if "API 할당량이 부족" in final_report or "LLM 호출 중 오류" in final_report:
            final_report = self._create_fallback_report(user_query, stock_data, analysis, recommendations)
        
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
    
    def _create_fallback_report(self, user_query: str, stock_data: Dict, analysis: str, recommendations: list) -> str:
        """LLM 호출 실패시 기본 보고서 생성"""
        report = "=== 투자 분석 보고서 ===\n\n"
        
        # 1. 요약
        report += "1. 요약 (Executive Summary)\n"
        report += f"질문: {user_query}\n"
        if stock_data:
            symbol = stock_data.get("symbol", "Unknown")
            current_price = stock_data.get("current_price", "N/A")
            report += f"분석 대상: {symbol} (현재가: ${current_price})\n"
        
        if analysis and not ("API 할당량이 부족" in analysis or "LLM 호출 중 오류" in analysis):
            report += f"분석 결과를 기반으로 투자 결정에 필요한 정보를 제공합니다.\n\n"
        else:
            report += f"기본 데이터 분석을 통한 참고 보고서입니다.\n\n"
        
        # 2. 주식 개요
        report += "2. 주식 개요 및 현재 상황\n"
        if stock_data:
            symbol = stock_data.get("symbol", "Unknown")
            current_price = stock_data.get("current_price", "N/A")
            change = stock_data.get("change", "N/A")
            change_percent = stock_data.get("change_percent", "N/A")
            volume = stock_data.get("volume", "N/A")
            
            report += f"주식 심볼: {symbol}\n"
            report += f"현재 가격: ${current_price}\n"
            if change != "N/A":
                report += f"변동: ${change} ({change_percent}%)\n"
            if volume != "N/A":
                report += f"거래량: {volume:,}\n"
        else:
            report += "주식 데이터를 가져올 수 없었습니다.\n"
        report += "\n"
        
        # 3. 핵심 분석 내용
        report += "3. 핵심 분석 내용\n"
        if analysis and not ("API 할당량이 부족" in analysis or "LLM 호출 중 오류" in analysis):
            # 분석 내용이 있으면 사용
            report += analysis + "\n"
        else:
            # 기본 분석 정보
            if stock_data:
                pe_ratio = stock_data.get("pe_ratio", "N/A")
                high_52w = stock_data.get("52w_high", "N/A")
                low_52w = stock_data.get("52w_low", "N/A")
                
                if pe_ratio != "N/A":
                    if pe_ratio < 15:
                        report += f"- PER {pe_ratio}로 상대적으로 저평가된 상태입니다.\n"
                    elif pe_ratio > 25:
                        report += f"- PER {pe_ratio}로 상대적으로 고평가된 상태입니다.\n"
                    else:
                        report += f"- PER {pe_ratio}로 적정 수준입니다.\n"
                
                if high_52w != "N/A" and low_52w != "N/A" and current_price != "N/A":
                    report += f"- 52주 범위: ${low_52w} ~ ${high_52w}\n"
            else:
                report += "상세 분석을 위한 데이터가 부족합니다.\n"
        report += "\n"
        
        # 4. 투자 추천사항
        report += "4. 투자 추천사항\n"
        if recommendations:
            for rec in recommendations:
                if isinstance(rec, str):
                    report += f"- {rec}\n"
                else:
                    report += f"- {rec}\n"
        else:
            report += "- 데이터 부족으로 구체적 추천을 제공할 수 없습니다.\n"
            report += "- 충분한 분석 후 투자 결정을 내리시길 권장합니다.\n"
        report += "\n"
        
        # 5. 리스크 및 주의사항
        report += "5. 리스크 및 주의사항\n"
        report += "- 투자에는 항상 리스크가 따릅니다.\n"
        report += "- 시장 변동성, 경제 상황, 기업 실적 변화 등 다양한 요인이 주가에 영향을 미칩니다.\n"
        report += "- 본 분석은 참고용이며, 투자 결정은 개인 책임입니다.\n"
        report += "- 투자 전 충분한 검토와 리스크 관리가 필요합니다.\n\n"
        
        # 6. 결론
        report += "6. 결론\n"
        report += "LLM 기반 상세 분석이 제한되었지만, 수집된 데이터를 통해 기본적인 투자 참고사항을 제공했습니다.\n"
        report += "최종 투자 결정은 추가적인 연구와 개인의 투자 목표를 고려하여 신중히 내리시기 바랍니다.\n\n"
        
        report += "---\n"
        report += "※ 본 보고서는 자동 생성된 기본 분석이며, 면책조항이 적용됩니다."
        
        return report
