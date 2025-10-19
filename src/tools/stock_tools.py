"""
주식 데이터 관련 도구들
Stock Data Tools
"""
import yfinance as yf
import requests
import time
import json
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class StockDataTool:
    """주식 데이터 조회 도구"""
    
    def __init__(self):
        self.name = "stock_data_tool"
        self.description = """
        주식 데이터를 조회합니다.
        
        입력: {
            "symbol": "주식 심볼 (예: AAPL, TSLA)"
        }
        
        출력: {
            "current_price": "현재 가격",
            "change": "변화량",
            "change_percent": "변화율",
            "volume": "거래량",
            "market_cap": "시가총액",
            "pe_ratio": "PER",
            "52w_high": "52주 최고가",
            "52w_low": "52주 최저가"
        }
        
        에러: 네트워크 오류, 잘못된 심볼 등
        """
    
    def run(self, symbol: str, max_retries: int = 3) -> Dict:
        """
        주식 데이터를 조회합니다.
        
        Args:
            symbol: 주식 심볼
            max_retries: 최대 재시도 횟수
            
        Returns:
            Dict: 주식 데이터 또는 에러 정보
        """
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                # 주요 데이터 추출
                stock_data = {
                    "symbol": symbol,
                    "current_price": info.get("currentPrice", "N/A"),
                    "change": info.get("regularMarketChange", "N/A"),
                    "change_percent": info.get("regularMarketChangePercent", "N/A"),
                    "volume": info.get("volume", "N/A"),
                    "market_cap": info.get("marketCap", "N/A"),
                    "pe_ratio": info.get("trailingPE", "N/A"),
                    "52w_high": info.get("fiftyTwoWeekHigh", "N/A"),
                    "52w_low": info.get("fiftyTwoWeekLow", "N/A"),
                    "status": "success"
                }
                
                latency_ms = (time.time() - start_time) * 1000
                logger.info({
                    "tool": self.name,
                    "symbol": symbol,
                    "status": "success",
                    "attempt": attempt + 1,
                    "latency_ms": latency_ms
                })
                
                return stock_data
                
            except Exception as e:
                latency_ms = (time.time() - start_time) * 1000
                error_msg = f"주식 데이터 조회 실패: {str(e)}"
                
                logger.error({
                    "tool": self.name,
                    "symbol": symbol,
                    "status": "error",
                    "error": error_msg,
                    "attempt": attempt + 1,
                    "latency_ms": latency_ms
                })
                
                if attempt == max_retries - 1:
                    return {
                        "symbol": symbol,
                        "status": "error",
                        "error": error_msg,
                        "retry_hint": "네트워크 연결을 확인하거나 심볼을 다시 확인해주세요."
                    }
                
                # 지수 백오프
                time.sleep(0.5 * (2 ** attempt))


class FinancialNewsTool:
    """금융 뉴스 조회 도구"""
    
    def __init__(self, tavily_api_key: Optional[str] = None):
        self.name = "financial_news_tool"
        self.tavily_api_key = tavily_api_key
        self.description = """
        금융 관련 뉴스를 검색합니다.
        
        입력: {
            "query": "검색 쿼리 (예: AAPL earnings)",
            "max_results": "최대 결과 수 (기본값: 5)"
        }
        
        출력: [
            {
                "title": "뉴스 제목",
                "url": "뉴스 링크",
                "snippet": "요약",
                "published_date": "발행일"
            }
        ]
        
        에러: API 키 없음, 네트워크 오류, 빈 결과
        """
    
    def run(self, query: str, max_results: int = 5, max_retries: int = 3) -> Dict:
        """
        금융 뉴스를 검색합니다.
        
        Args:
            query: 검색 쿼리
            max_results: 최대 결과 수
            max_retries: 최대 재시도 횟수
            
        Returns:
            Dict: 뉴스 데이터 또는 에러 정보
        """
        if not self.tavily_api_key:
            return {
                "status": "error",
                "error": "Tavily API 키가 설정되지 않았습니다.",
                "retry_hint": "API 키를 설정해주세요."
            }
        
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                
                headers = {
                    "Authorization": f"Bearer {self.tavily_api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "query": f"financial news {query}",
                    "max_results": max_results,
                    "include_domains": ["reuters.com", "bloomberg.com", "cnbc.com", "marketwatch.com"],
                    "search_depth": "advanced"
                }
                
                response = requests.post(
                    "https://api.tavily.com/search",
                    headers=headers,
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    
                    news_data = []
                    for result in results:
                        news_data.append({
                            "title": result.get("title", "N/A"),
                            "url": result.get("url", "N/A"),
                            "snippet": result.get("content", "N/A"),
                            "published_date": "N/A"  # Tavily에서는 제공하지 않음
                        })
                    
                    latency_ms = (time.time() - start_time) * 1000
                    logger.info({
                        "tool": self.name,
                        "query": query,
                        "status": "success",
                        "results_count": len(news_data),
                        "attempt": attempt + 1,
                        "latency_ms": latency_ms
                    })
                    
                    return {
                        "status": "success",
                        "query": query,
                        "results": news_data,
                        "total_results": len(news_data)
                    }
                    
                elif response.status_code >= 500:
                    # 5xx 에러 - 재시도
                    raise Exception(f"서버 에러: {response.status_code}")
                else:
                    # 4xx 에러 - 재시도하지 않음
                    return {
                        "status": "error",
                        "error": f"클라이언트 에러: {response.status_code}",
                        "retry_hint": "검색 쿼리를 수정해보세요."
                    }
                    
            except Exception as e:
                latency_ms = (time.time() - start_time) * 1000
                error_msg = f"뉴스 검색 실패: {str(e)}"
                
                logger.error({
                    "tool": self.name,
                    "query": query,
                    "status": "error",
                    "error": error_msg,
                    "attempt": attempt + 1,
                    "latency_ms": latency_ms
                })
                
                if attempt == max_retries - 1:
                    return {
                        "status": "error",
                        "error": error_msg,
                        "retry_hint": "네트워크 연결을 확인하거나 검색어를 수정해보세요."
                    }
                
                time.sleep(0.5 * (2 ** attempt))
        
        return {
            "status": "error",
            "error": "최대 재시도 횟수 초과",
            "retry_hint": "나중에 다시 시도해주세요."
        }
