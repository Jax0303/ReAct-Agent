"""
데이터 정규화 및 요약 유틸리티
Data Normalization and Summarization Utility
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class DataNormalizer:
    """툴 결과를 요약하고 정규화하는 클래스"""
    
    @staticmethod
    def normalize_stock_data(raw_data: Dict) -> Dict:
        """
        주식 데이터를 정규화하고 요약
        
        Args:
            raw_data: yfinance에서 가져온 원시 데이터
            
        Returns:
            정규화된 주식 데이터
        """
        if raw_data.get("status") != "success":
            return {
                "status": "error",
                "error": raw_data.get("error", "Unknown error"),
                "normalized_at": datetime.now().isoformat()
            }
        
        try:
            # 가격 정보 정규화
            current_price = raw_data.get("current_price", 0)
            change = raw_data.get("change", 0)
            change_percent = raw_data.get("change_percent", 0)
            
            # 추세 판단
            if change > 0:
                trend = "상승"
                trend_emoji = "📈"
            elif change < 0:
                trend = "하락"
                trend_emoji = "📉"
            else:
                trend = "보합"
                trend_emoji = "➡️"
            
            # PER 평가
            pe_ratio = raw_data.get("pe_ratio", "N/A")
            if pe_ratio != "N/A" and isinstance(pe_ratio, (int, float)):
                if pe_ratio < 15:
                    pe_evaluation = "저평가"
                elif pe_ratio > 25:
                    pe_evaluation = "고평가"
                else:
                    pe_evaluation = "적정"
            else:
                pe_evaluation = "평가불가"
            
            # 52주 범위 내 위치 계산
            high_52w = raw_data.get("52w_high")
            low_52w = raw_data.get("52w_low")
            
            if high_52w and low_52w and current_price:
                range_position = ((current_price - low_52w) / (high_52w - low_52w)) * 100
                
                if range_position > 80:
                    position_desc = "고점권"
                elif range_position < 20:
                    position_desc = "저점권"
                else:
                    position_desc = "중간권"
            else:
                range_position = None
                position_desc = "알 수 없음"
            
            # 정규화된 데이터
            normalized = {
                "status": "success",
                "symbol": raw_data.get("symbol"),
                "timestamp": datetime.now().isoformat(),
                
                # 가격 정보 (요약)
                "price_summary": {
                    "current": current_price,
                    "change": change,
                    "change_percent": change_percent,
                    "trend": trend,
                    "trend_emoji": trend_emoji
                },
                
                # 밸류에이션 (요약)
                "valuation_summary": {
                    "pe_ratio": pe_ratio,
                    "pe_evaluation": pe_evaluation,
                    "market_cap": raw_data.get("market_cap")
                },
                
                # 거래 정보 (요약)
                "trading_summary": {
                    "volume": raw_data.get("volume"),
                    "volume_formatted": f"{raw_data.get('volume', 0):,}" if raw_data.get('volume') else "N/A"
                },
                
                # 52주 범위 (요약)
                "range_summary": {
                    "high_52w": high_52w,
                    "low_52w": low_52w,
                    "position_percent": round(range_position, 1) if range_position else None,
                    "position_description": position_desc
                },
                
                # 원시 데이터 (참고용)
                "_raw": raw_data
            }
            
            logger.info({
                "normalizer": "stock_data",
                "symbol": raw_data.get("symbol"),
                "trend": trend,
                "pe_evaluation": pe_evaluation,
                "position": position_desc
            })
            
            return normalized
            
        except Exception as e:
            logger.error({
                "normalizer": "stock_data",
                "error": str(e),
                "raw_data_keys": list(raw_data.keys()) if isinstance(raw_data, dict) else "not_dict"
            })
            
            return {
                "status": "error",
                "error": f"정규화 실패: {str(e)}",
                "normalized_at": datetime.now().isoformat()
            }
    
    @staticmethod
    def normalize_news_data(raw_data: Dict) -> Dict:
        """
        뉴스 데이터를 정규화하고 요약
        
        Args:
            raw_data: Tavily에서 가져온 원시 뉴스 데이터
            
        Returns:
            정규화된 뉴스 데이터
        """
        if raw_data.get("status") != "success":
            return {
                "status": "error",
                "error": raw_data.get("error", "Unknown error"),
                "normalized_at": datetime.now().isoformat()
            }
        
        try:
            results = raw_data.get("results", [])
            
            # 뉴스 요약
            news_summary = []
            sentiment_keywords = {
                "positive": ["상승", "증가", "성장", "호조", "긍정", "strong", "rise", "gain"],
                "negative": ["하락", "감소", "우려", "부진", "약세", "weak", "fall", "drop"]
            }
            
            sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
            
            for news in results[:10]:  # 최대 10개만 처리
                title = news.get("title", "")
                snippet = news.get("snippet", "")
                
                # 감성 분석 (간단한 키워드 기반)
                text = (title + " " + snippet).lower()
                pos_count = sum(1 for word in sentiment_keywords["positive"] if word in text)
                neg_count = sum(1 for word in sentiment_keywords["negative"] if word in text)
                
                if pos_count > neg_count:
                    sentiment = "positive"
                    sentiment_emoji = "✅"
                elif neg_count > pos_count:
                    sentiment = "negative"
                    sentiment_emoji = "⚠️"
                else:
                    sentiment = "neutral"
                    sentiment_emoji = "ℹ️"
                
                sentiment_counts[sentiment] += 1
                
                news_summary.append({
                    "title": title[:100],  # 제목 100자 제한
                    "snippet": snippet[:200],  # 요약 200자 제한
                    "url": news.get("url"),
                    "sentiment": sentiment,
                    "sentiment_emoji": sentiment_emoji
                })
            
            # 전체 감성 판단
            if sentiment_counts["positive"] > sentiment_counts["negative"]:
                overall_sentiment = "긍정적"
                overall_emoji = "📈"
            elif sentiment_counts["negative"] > sentiment_counts["positive"]:
                overall_sentiment = "부정적"
                overall_emoji = "📉"
            else:
                overall_sentiment = "중립적"
                overall_emoji = "➡️"
            
            normalized = {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                
                # 뉴스 개요
                "news_overview": {
                    "total_count": len(results),
                    "processed_count": len(news_summary),
                    "overall_sentiment": overall_sentiment,
                    "overall_emoji": overall_emoji,
                    "sentiment_breakdown": sentiment_counts
                },
                
                # 요약된 뉴스 목록
                "news_items": news_summary,
                
                # 원시 데이터 (참고용)
                "_raw": raw_data
            }
            
            logger.info({
                "normalizer": "news_data",
                "total_news": len(results),
                "processed": len(news_summary),
                "overall_sentiment": overall_sentiment,
                "sentiment_breakdown": sentiment_counts
            })
            
            return normalized
            
        except Exception as e:
            logger.error({
                "normalizer": "news_data",
                "error": str(e)
            })
            
            return {
                "status": "error",
                "error": f"정규화 실패: {str(e)}",
                "normalized_at": datetime.now().isoformat()
            }
    
    @staticmethod
    def normalize_calculation_result(raw_data: Dict) -> Dict:
        """
        계산 결과를 정규화
        
        Args:
            raw_data: 계산기 툴의 원시 결과
            
        Returns:
            정규화된 계산 결과
        """
        if raw_data.get("status") != "success":
            return {
                "status": "error",
                "error": raw_data.get("error", "Unknown error"),
                "expression": raw_data.get("expression", ""),
                "normalized_at": datetime.now().isoformat()
            }
        
        try:
            result = raw_data.get("result")
            expression = raw_data.get("expression", "")
            
            # 결과 포맷팅
            if isinstance(result, float):
                formatted_result = f"{result:,.2f}"
            else:
                formatted_result = str(result)
            
            normalized = {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "calculation": {
                    "expression": expression,
                    "result": result,
                    "formatted_result": formatted_result
                },
                "_raw": raw_data
            }
            
            logger.info({
                "normalizer": "calculation",
                "expression": expression,
                "result": result
            })
            
            return normalized
            
        except Exception as e:
            logger.error({
                "normalizer": "calculation",
                "error": str(e)
            })
            
            return {
                "status": "error",
                "error": f"정규화 실패: {str(e)}",
                "normalized_at": datetime.now().isoformat()
            }

