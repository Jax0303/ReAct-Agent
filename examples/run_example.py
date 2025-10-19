#!/usr/bin/env python3
"""
금융 ReAct 에이전트 실행 예제
Financial ReAct Agent Run Example
"""
import sys
import os
import asyncio
import logging

# 프로젝트 루트를 파이썬 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from workflows.financial_workflow import FinancialWorkflow
from utils.config import Config

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def run_financial_analysis():
    """금융 분석 실행"""
    
    # 설정 검증
    if not Config.validate_config():
        logger.error("설정 검증 실패. .env 파일을 확인해주세요.")
        return
    
    # 워크플로우 초기화
    workflow = FinancialWorkflow(
        openai_api_key=Config.OPENAI_API_KEY,
        tavily_api_key=Config.TAVILY_API_KEY
    )
    
    # 사용자 입력받기
    print("=== 금융 ReAct 에이전트 ===")
    print("주식 분석을 위한 정보를 입력해주세요.")
    
    stock_symbol = input("주식 심볼을 입력하세요 (예: AAPL, TSLA): ").strip().upper()
    if not stock_symbol:
        stock_symbol = "AAPL"  # 기본값
    
    user_query = input(f"{stock_symbol}에 대한 질문을 입력하세요: ").strip()
    if not user_query:
        user_query = f"{stock_symbol} 주식에 대한 투자 분석과 추천을 해주세요."
    
    print(f"\n분석을 시작합니다...\n")
    print(f"주식 심볼: {stock_symbol}")
    print(f"질문: {user_query}")
    print("-" * 50)
    
    # 초기 상태 설정
    initial_state = {
        "messages": [
            {
                "role": "user",
                "content": user_query
            }
        ],
        "stock_symbol": stock_symbol,
        "user_query": user_query,
        "iteration": 0,
        "max_iterations": Config.DEFAULT_MAX_ITERATIONS,
        "status": "researching",
        "errors": [],
        "tool_history": [],
        "stock_data": None,
        "market_data": None,
        "news_data": [],
        "analysis": None,
        "recommendations": None,
        "final_report": ""
    }
    
    try:
        # 워크플로우 실행
        result = workflow.run(initial_state)
        
        # 결과 출력
        print("\n=== 분석 결과 ===")
        print(f"최종 상태: {result.get('status', 'unknown')}")
        print(f"반복 횟수: {result.get('iteration', 0)}")
        
        # 에러가 있었다면 출력
        errors = result.get('errors', [])
        if errors:
            print(f"\n발생한 에러들:")
            for i, error in enumerate(errors, 1):
                print(f"{i}. {error}")
        
        # 주요 메시지들 출력
        messages = result.get('messages', [])
        print(f"\n처리 과정:")
        for i, msg in enumerate(messages[-5:], 1):  # 마지막 5개 메시지만
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')[:200]  # 처음 200자만
            print(f"{i}. [{role}] {content}...")
        
        # 최종 보고서 출력
        final_report = result.get('final_report', '')
        if final_report:
            print(f"\n=== 최종 보고서 ===")
            print(final_report)
        else:
            print("\n최종 보고서가 생성되지 않았습니다.")
        
        # 도구 사용 히스토리
        tool_history = result.get('tool_history', [])
        if tool_history:
            print(f"\n=== 사용된 도구들 ===")
            for i, tool_usage in enumerate(tool_history, 1):
                tool_name = tool_usage.get('tool', 'unknown')
                print(f"{i}. {tool_name}")
        
    except Exception as e:
        logger.error(f"워크플로우 실행 중 오류 발생: {str(e)}")
        print(f"\n오류가 발생했습니다: {str(e)}")


def run_interactive_mode():
    """대화형 모드"""
    print("=== 대화형 금융 분석 모드 ===")
    print("종료하려면 'quit' 또는 'exit'를 입력하세요.\n")
    
    # 설정 검증
    if not Config.validate_config():
        print("설정 검증 실패. .env 파일을 확인해주세요.")
        return
    
    workflow = FinancialWorkflow(
        openai_api_key=Config.OPENAI_API_KEY,
        tavily_api_key=Config.TAVILY_API_KEY
    )
    
    while True:
        try:
            user_input = input("\n질문을 입력하세요 (예: AAPL 분석): ").strip()
            
            if user_input.lower() in ['quit', 'exit', '종료']:
                print("프로그램을 종료합니다.")
                break
            
            if not user_input:
                continue
            
            # 간단한 파싱 (주식 심볼 추출)
            words = user_input.split()
            stock_symbol = None
            
            for word in words:
                if word.isupper() and len(word) <= 5 and word.isalpha():
                    stock_symbol = word
                    break
            
            if not stock_symbol:
                stock_symbol = input("주식 심볼을 입력하세요: ").strip().upper()
                if not stock_symbol:
                    continue
            
            # 워크플로우 실행
            initial_state = {
                "messages": [{"role": "user", "content": user_input}],
                "stock_symbol": stock_symbol,
                "user_query": user_input,
                "iteration": 0,
                "max_iterations": 2,  # 대화형 모드에서는 빠른 응답을 위해 제한
                "status": "researching",
                "errors": [],
                "tool_history": [],
                "final_report": ""
            }
            
            print(f"\n{stock_symbol} 분석 중...")
            result = workflow.run(initial_state)
            
            # 간단한 결과 출력
            final_report = result.get('final_report', '')
            if final_report:
                print("\n--- 분석 결과 ---")
                print(final_report[:500] + "..." if len(final_report) > 500 else final_report)
            else:
                print("분석 결과를 생성할 수 없었습니다.")
                
        except KeyboardInterrupt:
            print("\n\n프로그램을 종료합니다.")
            break
        except Exception as e:
            print(f"\n오류 발생: {str(e)}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="금융 ReAct 에이전트")
    parser.add_argument("--interactive", "-i", action="store_true", 
                       help="대화형 모드로 실행")
    
    args = parser.parse_args()
    
    if args.interactive:
        run_interactive_mode()
    else:
        run_financial_analysis()
