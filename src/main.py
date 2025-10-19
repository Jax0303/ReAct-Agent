"""
ReAct 금융 분석 에이전트 메인 실행 파일
Main Entry Point for ReAct Financial Analysis Agent
"""
import os
import sys
import logging
import json
from datetime import datetime
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 경로 설정
sys.path.insert(0, os.path.dirname(__file__))

from workflows.financial_workflow import FinancialWorkflow
from utils.config import Config

# 로깅 설정 (구조적 로그)
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',  # JSON 로그를 위해 간단한 포맷 사용
    handlers=[
        logging.FileHandler('financial_agent.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class StructuredLogger:
    """구조적 로그를 위한 로거"""
    
    @staticmethod
    def log(level: str, data: dict):
        """
        구조적 로그 출력
        
        Args:
            level: 로그 레벨 (INFO, WARNING, ERROR 등)
            data: 로그 데이터 (dict)
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            **data
        }
        
        # JSON 형식으로 로그 출력
        log_json = json.dumps(log_entry, ensure_ascii=False, indent=2)
        
        if level == "INFO":
            logger.info(log_json)
        elif level == "WARNING":
            logger.warning(log_json)
        elif level == "ERROR":
            logger.error(log_json)
        else:
            logger.debug(log_json)


def print_welcome():
    """환영 메시지 출력"""
    print("\n" + "="*70)
    print("🚀 ReAct 금융 분석 에이전트 (Google Gemini 2.0 Flash 기반)")
    print("="*70)
    print("\n📊 이 에이전트는 다음을 수행합니다:")
    print("   1. 주식 데이터 수집 (yfinance)")
    print("   2. 금융 뉴스 수집 (Tavily)")
    print("   3. AI 기반 분석 (Google Gemini)")
    print("   4. 투자 추천사항 생성")
    print("   5. 최종 보고서 작성")
    print("\n" + "-"*70 + "\n")


def print_result_summary(result: dict):
    """결과 요약 출력"""
    print("\n" + "="*70)
    print("📋 분석 결과 요약")
    print("="*70)
    
    # 주식 데이터 요약
    stock_data = result.get("stock_data", {})
    if stock_data and stock_data.get("status") == "success":
        price_summary = stock_data.get("price_summary", {})
        valuation = stock_data.get("valuation_summary", {})
        
        print(f"\n📈 주식 정보:")
        print(f"   - 심볼: {stock_data.get('symbol', 'N/A')}")
        print(f"   - 현재가: ${price_summary.get('current', 'N/A')}")
        print(f"   - 변동: {price_summary.get('change', 'N/A')} ({price_summary.get('change_percent', 'N/A')}%)")
        print(f"   - 추세: {price_summary.get('trend_emoji', '')} {price_summary.get('trend', 'N/A')}")
        print(f"   - PER: {valuation.get('pe_ratio', 'N/A')} ({valuation.get('pe_evaluation', 'N/A')})")
    
    # 뉴스 데이터 요약
    news_data = result.get("news_data", {})
    if news_data and news_data.get("status") == "success":
        news_overview = news_data.get("news_overview", {})
        
        print(f"\n📰 뉴스 정보:")
        print(f"   - 뉴스 개수: {news_overview.get('processed_count', 0)}개")
        print(f"   - 전체 감성: {news_overview.get('overall_emoji', '')} {news_overview.get('overall_sentiment', 'N/A')}")
        
        sentiment_breakdown = news_overview.get('sentiment_breakdown', {})
        print(f"   - 긍정: {sentiment_breakdown.get('positive', 0)}개")
        print(f"   - 부정: {sentiment_breakdown.get('negative', 0)}개")
        print(f"   - 중립: {sentiment_breakdown.get('neutral', 0)}개")
    
    # 추천사항
    recommendations = result.get("recommendations", [])
    if recommendations:
        print(f"\n💡 투자 추천사항 ({len(recommendations)}개):")
        for i, rec in enumerate(recommendations[:5], 1):
            print(f"   {i}. {rec}")
    
    # 최종 보고서
    final_report = result.get("final_report", "")
    if final_report:
        print(f"\n📝 최종 보고서:")
        print(f"   {final_report[:300]}...")
    
    # 에러 정보
    errors = result.get("errors", [])
    if errors:
        print(f"\n⚠️ 경고/오류 ({len(errors)}개):")
        for error in errors[:3]:
            print(f"   - {error}")
    
    print("\n" + "="*70 + "\n")


def run_interactive_mode(workflow: FinancialWorkflow):
    """대화형 모드 실행"""
    StructuredLogger.log("INFO", {
        "mode": "interactive",
        "status": "started"
    })
    
    while True:
        try:
            # 사용자 입력
            stock_symbol = input("🔍 분석할 주식 심볼을 입력하세요 (종료: 'quit'): ").strip().upper()
            
            if stock_symbol in ["QUIT", "EXIT", "Q"]:
                StructuredLogger.log("INFO", {
                    "mode": "interactive",
                    "status": "user_exit"
                })
                print("\n👋 프로그램을 종료합니다.")
                break
            
            if not stock_symbol:
                print("⚠️ 주식 심볼을 입력해주세요.\n")
                continue
            
            # 워크플로우 실행
            StructuredLogger.log("INFO", {
                "mode": "interactive",
                "action": "analysis_started",
                "symbol": stock_symbol
            })
            
            print(f"\n🔄 {stock_symbol} 분석 시작...\n")
            
            initial_state = {
                "stock_symbol": stock_symbol,
                "user_query": f"Analyze {stock_symbol} stock",
                "messages": [],
                "iteration": 0,
                "max_iterations": 3
            }
            
            result = workflow.run(initial_state)
            
            # 결과 출력
            print_result_summary(result)
            
            StructuredLogger.log("INFO", {
                "mode": "interactive",
                "action": "analysis_completed",
                "symbol": stock_symbol,
                "status": result.get("status", "unknown"),
                "errors_count": len(result.get("errors", []))
            })
            
        except KeyboardInterrupt:
            StructuredLogger.log("WARNING", {
                "mode": "interactive",
                "status": "interrupted",
                "reason": "keyboard_interrupt"
            })
            print("\n\n⚠️ 사용자에 의해 중단되었습니다.")
            break
        except Exception as e:
            StructuredLogger.log("ERROR", {
                "mode": "interactive",
                "error": str(e),
                "error_type": type(e).__name__
            })
            print(f"\n❌ 오류 발생: {str(e)}\n")


def run_streaming_mode(workflow: FinancialWorkflow, stock_symbol: str):
    """스트리밍 모드 실행"""
    StructuredLogger.log("INFO", {
        "mode": "streaming",
        "status": "started",
        "symbol": stock_symbol
    })
    
    print(f"\n🔄 {stock_symbol} 스트리밍 분석 시작...\n")
    
    initial_state = {
        "stock_symbol": stock_symbol,
        "user_query": f"Analyze {stock_symbol} stock",
        "messages": [],
        "iteration": 0,
        "max_iterations": 3
    }
    
    try:
        for event in workflow.stream(initial_state):
            node = event.get("node", "unknown")
            status = event.get("status", "running")
            
            # 노드별 이모지
            node_emojis = {
                "research": "🔍",
                "analyze": "📊",
                "recommend": "💡",
                "human_approval": "✋",
                "review": "📝",
                "error": "❌"
            }
            
            emoji = node_emojis.get(node, "⚙️")
            
            print(f"{emoji} {node.upper()} - {status}")
            
            StructuredLogger.log("INFO", {
                "mode": "streaming",
                "node": node,
                "status": status
            })
        
        print("\n✅ 스트리밍 분석 완료!\n")
        
        StructuredLogger.log("INFO", {
            "mode": "streaming",
            "status": "completed",
            "symbol": stock_symbol
        })
        
    except Exception as e:
        StructuredLogger.log("ERROR", {
            "mode": "streaming",
            "error": str(e),
            "error_type": type(e).__name__
        })
        print(f"\n❌ 스트리밍 오류: {str(e)}\n")


def main():
    """메인 함수"""
    # 환영 메시지
    print_welcome()
    
    # 설정 검증
    StructuredLogger.log("INFO", {
        "action": "config_validation",
        "status": "starting"
    })
    
    if not Config.validate_config():
        StructuredLogger.log("ERROR", {
            "action": "config_validation",
            "status": "failed",
            "error": "API 키 설정 필요"
        })
        print("❌ 설정 오류: GOOGLE_AI_API_KEY 또는 OPENAI_API_KEY가 필요합니다.")
        print("💡 .env 파일을 확인하고 필요한 API 키를 설정해주세요.")
        sys.exit(1)
    
    StructuredLogger.log("INFO", {
        "action": "config_validation",
        "status": "success"
    })
    
    # API 키 가져오기
    google_ai_api_key = os.getenv("GOOGLE_AI_API_KEY")
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    
    # 워크플로우 초기화
    StructuredLogger.log("INFO", {
        "action": "workflow_initialization",
        "status": "starting"
    })
    
    try:
        workflow = FinancialWorkflow(google_ai_api_key, tavily_api_key)
        StructuredLogger.log("INFO", {
            "action": "workflow_initialization",
            "status": "success"
        })
    except Exception as e:
        StructuredLogger.log("ERROR", {
            "action": "workflow_initialization",
            "status": "failed",
            "error": str(e)
        })
        print(f"❌ 워크플로우 초기화 실패: {str(e)}")
        sys.exit(1)
    
    # 실행 모드 선택
    if len(sys.argv) > 1:
        # 명령줄 인수로 주식 심볼이 제공된 경우
        stock_symbol = sys.argv[1].upper()
        mode = sys.argv[2] if len(sys.argv) > 2 else "normal"
        
        StructuredLogger.log("INFO", {
            "mode": mode,
            "symbol": stock_symbol,
            "source": "command_line"
        })
        
        if mode == "stream":
            run_streaming_mode(workflow, stock_symbol)
        else:
            initial_state = {
                "stock_symbol": stock_symbol,
                "user_query": f"Analyze {stock_symbol} stock",
                "messages": [],
                "iteration": 0,
                "max_iterations": 3
            }
            result = workflow.run(initial_state)
            print_result_summary(result)
    else:
        # 대화형 모드
        run_interactive_mode(workflow)


if __name__ == "__main__":
    main()

