"""
계산기 도구
Calculator Tool
"""
import re
import math
import time
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class CalculatorTool:
    """안전한 수학 계산 도구"""
    
    def __init__(self):
        self.name = "calculator_tool"
        self.description = """
        수학 계산을 수행합니다.
        
        입력: {
            "expression": "계산식 문자열 (예: '2 + 3 * 4')"
        }
        
        출력: {
            "result": "계산 결과",
            "expression": "입력 식"
        }
        
        에러: 잘못된 수식, 나누기 0, 지원되지 않는 연산자
        """
    
    def run(self, expression: str) -> Dict[str, Any]:
        """
        수학 계산을 수행합니다.
        
        Args:
            expression: 계산할 수식 문자열
            
        Returns:
            Dict: 계산 결과 또는 에러 정보
        """
        try:
            start_time = time.time()
            
            # 안전한 문자만 허용
            allowed_chars = r'[0-9+\-*/().\s]'
            if not re.match(f'^{allowed_chars}+$', expression):
                return {
                    "status": "error",
                    "error": "허용되지 않는 문자가 포함되어 있습니다.",
                    "expression": expression,
                    "retry_hint": "숫자와 기본 연산자(+, -, *, /, 괄호)만 사용하세요."
                }
            
            # 위험한 함수 제거를 위한 추가 검증
            dangerous_patterns = ['import', 'exec', 'eval', '__', 'open', 'file']
            if any(pattern in expression.lower() for pattern in dangerous_patterns):
                return {
                    "status": "error",
                    "error": "위험한 패턴이 감지되었습니다.",
                    "expression": expression,
                    "retry_hint": "기본 수학 연산만 사용하세요."
                }
            
            # 실제 계산 (제한된 스코프에서)
            safe_globals = {
                '__builtins__': {},
                'math': math,
                'pi': math.pi,
                'e': math.e
            }
            
            # 수식 평가 전 추가 검증
            try:
                result = eval(expression, safe_globals)
                
                # 결과가 숫자인지 확인
                if not isinstance(result, (int, float)):
                    raise ValueError("계산 결과가 숫자가 아닙니다.")
                
                # 무한대나 NaN 체크
                if math.isnan(result) or math.isinf(result):
                    raise ValueError("계산 결과가 유효하지 않습니다.")
                
                latency_ms = (time.time() - start_time) * 1000
                logger.info({
                    "tool": self.name,
                    "expression": expression,
                    "result": result,
                    "status": "success",
                    "latency_ms": latency_ms
                })
                
                return {
                    "status": "success",
                    "result": result,
                    "expression": expression
                }
                
            except ZeroDivisionError:
                return {
                    "status": "error",
                    "error": "0으로 나눌 수 없습니다.",
                    "expression": expression,
                    "retry_hint": "계산식을 확인해주세요."
                }
            except Exception as calc_error:
                return {
                    "status": "error",
                    "error": f"계산 오류: {str(calc_error)}",
                    "expression": expression,
                    "retry_hint": "수식을 다시 확인해주세요."
                }
                
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.error({
                "tool": self.name,
                "expression": expression,
                "status": "error",
                "error": str(e),
                "latency_ms": latency_ms
            })
            
            return {
                "status": "error",
                "error": f"계산 도구 오류: {str(e)}",
                "expression": expression,
                "retry_hint": "올바른 수식을 입력해주세요."
            }


