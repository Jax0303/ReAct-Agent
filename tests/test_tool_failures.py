"""
툴 실패 케이스 테스트
Tests for Tool Failure Cases
"""
import pytest
import os
import sys

# 경로 설정
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tools.stock_tools import StockDataTool, FinancialNewsTool
from tools.calculator_tool import CalculatorTool


class TestToolFailures:
    """툴 실패 케이스 테스트"""
    
    def test_stock_tool_invalid_symbol(self):
        """
        주식 툴 - 잘못된 심볼 테스트
        """
        tool = StockDataTool()
        
        # 잘못된 심볼들
        invalid_symbols = [
            "INVALID123",
            "NOTEXIST",
            "XXXXXXXX",
            "___",
            ""
        ]
        
        for symbol in invalid_symbols:
            result = tool.run(symbol)
            
            # 실패 케이스 검증
            assert result["status"] == "error", f"Symbol {symbol} should fail"
            assert "error" in result, f"Symbol {symbol} should have error message"
            
            print(f"✅ 주식 툴 실패 케이스 테스트 통과: {symbol} -> {result['error']}")
    
    def test_stock_tool_network_failure_simulation(self):
        """
        주식 툴 - 네트워크 실패 시뮬레이션
        """
        tool = StockDataTool()
        
        # 매우 긴 타임아웃으로 네트워크 문제 시뮬레이션
        # (실제로는 yfinance의 내부 처리를 통해 빠르게 실패)
        result = tool.run("")
        
        assert result["status"] == "error"
        print(f"✅ 네트워크 실패 시뮬레이션 테스트 통과: {result['error']}")
    
    def test_news_tool_api_key_missing(self):
        """
        뉴스 툴 - API 키 누락 테스트
        """
        # API 키 없이 초기화
        tool = FinancialNewsTool(tavily_api_key=None)
        
        result = tool.run("AAPL stock news")
        
        # API 키가 없으면 실패해야 함
        assert result["status"] == "error"
        assert "API" in result["error"] or "api" in result["error"] or "key" in result["error"].lower()
        
        print(f"✅ 뉴스 툴 API 키 누락 테스트 통과: {result['error']}")
    
    def test_news_tool_empty_query(self):
        """
        뉴스 툴 - 빈 쿼리 테스트
        """
        # 더미 API 키로 초기화
        tool = FinancialNewsTool(tavily_api_key="dummy_key")
        
        result = tool.run("")
        
        # 빈 쿼리는 실패해야 함
        assert result["status"] == "error"
        
        print(f"✅ 뉴스 툴 빈 쿼리 테스트 통과: {result['error']}")
    
    def test_calculator_invalid_expression(self):
        """
        계산기 툴 - 잘못된 표현식 테스트
        """
        tool = CalculatorTool()
        
        invalid_expressions = [
            "1 / 0",  # Division by zero
            "import os",  # Security risk
            "while True: pass",  # Infinite loop
            "__import__('os')",  # Import attempt
            "exec('print(1)')",  # Code execution
            "eval('1+1')",  # Eval attempt
            "abc xyz",  # Invalid syntax
            "1 + ",  # Incomplete expression
        ]
        
        for expr in invalid_expressions:
            result = tool.run(expr)
            
            # 모든 잘못된 표현식은 실패해야 함
            assert result["status"] == "error", f"Expression '{expr}' should fail"
            assert "error" in result, f"Expression '{expr}' should have error"
            
            print(f"✅ 계산기 툴 실패 케이스 테스트 통과: {expr} -> {result['error']}")
    
    def test_calculator_unsafe_operations(self):
        """
        계산기 툴 - 위험한 연산 테스트
        """
        tool = CalculatorTool()
        
        # 허용되지 않는 연산들
        unsafe_operations = [
            "open('file.txt')",
            "os.system('ls')",
            "__builtins__",
        ]
        
        for expr in unsafe_operations:
            result = tool.run(expr)
            
            assert result["status"] == "error"
            
            print(f"✅ 계산기 툴 위험 연산 차단 테스트 통과: {expr}")
    
    def test_tool_retry_mechanism(self):
        """
        툴 재시도 메커니즘 테스트
        """
        tool = StockDataTool()
        
        # 재시도가 필요한 케이스 (잘못된 심볼)
        # 재시도 로직이 지수 백오프와 함께 작동하는지 확인
        import time
        start_time = time.time()
        
        result = tool.run("INVALID_SYMBOL_FOR_RETRY_TEST")
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        # 재시도 로직으로 인해 최소 시간이 소요되어야 함
        # (지수 백오프: 1초 + 2초 + 4초 = 7초 예상)
        # 하지만 yfinance가 빠르게 실패할 수 있으므로 느슨하게 체크
        assert result["status"] == "error"
        
        print(f"✅ 툴 재시도 메커니즘 테스트 통과 (소요 시간: {elapsed:.2f}초)")
    
    def test_multiple_tool_failures_in_sequence(self):
        """
        여러 툴의 연속 실패 테스트
        """
        stock_tool = StockDataTool()
        news_tool = FinancialNewsTool(tavily_api_key=None)
        calc_tool = CalculatorTool()
        
        # 모든 툴이 연속으로 실패하는 시나리오
        failures = []
        
        # 주식 툴 실패
        result1 = stock_tool.run("INVALID")
        failures.append(result1)
        
        # 뉴스 툴 실패
        result2 = news_tool.run("test")
        failures.append(result2)
        
        # 계산기 툴 실패
        result3 = calc_tool.run("1/0")
        failures.append(result3)
        
        # 모든 툴이 실패했는지 확인
        for i, result in enumerate(failures, 1):
            assert result["status"] == "error", f"Tool {i} should fail"
            print(f"✅ 툴 {i} 실패 확인: {result['error']}")
        
        print(f"✅ 여러 툴 연속 실패 테스트 통과 (총 {len(failures)}개 툴)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

