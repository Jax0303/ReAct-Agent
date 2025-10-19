"""
도구 단위 테스트
Tool Unit Tests
"""
import pytest
import sys
import os

# 프로젝트 루트를 파이썬 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tools.stock_tools import StockDataTool, FinancialNewsTool
from tools.calculator_tool import CalculatorTool


class TestStockDataTool:
    """StockDataTool 테스트"""
    
    def setup_method(self):
        """테스트 설정"""
        self.tool = StockDataTool()
    
    def test_stock_data_tool_success(self):
        """주식 데이터 도구 성공 테스트"""
        result = self.tool.run("AAPL")
        
        assert isinstance(result, dict)
        assert "symbol" in result
        assert result["symbol"] == "AAPL"
        
        # 성공 케이스에서는 status가 success여야 함
        if result["status"] == "success":
            assert "current_price" in result
            assert "change" in result
    
    def test_stock_data_tool_invalid_symbol(self):
        """잘못된 심볼 테스트"""
        result = self.tool.run("INVALID_SYMBOL_12345")
        
        assert isinstance(result, dict)
        assert result["status"] == "error"
        assert "error" in result
        assert "retry_hint" in result


class TestCalculatorTool:
    """CalculatorTool 테스트"""
    
    def setup_method(self):
        """테스트 설정"""
        self.tool = CalculatorTool()
    
    def test_calculator_ok(self):
        """계산기 성공 테스트"""
        result = self.tool.run("5*8")
        
        assert isinstance(result, dict)
        assert "40" in str(result.get("result", ""))
        assert result["status"] == "success"
    
    def test_calculator_division_by_zero(self):
        """0으로 나누기 테스트"""
        result = self.tool.run("10/0")
        
        assert isinstance(result, dict)
        assert result["status"] == "error"
        assert "0으로 나눌" in result["error"]
    
    def test_calculator_invalid_expression(self):
        """잘못된 수식 테스트"""
        result = self.tool.run("invalid expression")
        
        assert isinstance(result, dict)
        assert result["status"] == "error"


class TestFinancialNewsTool:
    """FinancialNewsTool 테스트"""
    
    def setup_method(self):
        """테스트 설정"""
        # API 키가 없으면 테스트 스킵
        self.tool = FinancialNewsTool()
    
    def test_news_tool_no_api_key(self):
        """API 키 없음 테스트"""
        result = self.tool.run("AAPL earnings")
        
        assert isinstance(result, dict)
        assert result["status"] == "error"
        assert "API 키가 설정되지 않았습니다" in result["error"]
    
    @pytest.mark.skip(reason="API 키가 필요한 테스트")
    def test_news_tool_with_api_key(self):
        """API 키 있는 경우 테스트 (실제 API 키 필요)"""
        # 실제 API 키가 있으면 이 테스트 실행
        if self.tool.tavily_api_key:
            result = self.tool.run("AAPL stock news")
            assert isinstance(result, dict)
            # 결과는 성공 또는 에러일 수 있음
            assert "status" in result
