# API Documentation

## 도구/엔드포인트 명세서

### 1. StockDataTool

#### 입력
```json
{
    "symbol": "주식 심볼 (예: AAPL, TSLA)"
}
```

#### 출력
```json
{
    "symbol": "AAPL",
    "current_price": 150.25,
    "change": 2.15,
    "change_percent": 0.0145,
    "volume": 78456234,
    "market_cap": 2500000000000,
    "pe_ratio": 25.5,
    "52w_high": 182.94,
    "52w_low": 124.17,
    "status": "success"
}
```

#### 에러 응답
```json
{
    "symbol": "INVALID",
    "status": "error",
    "error": "주식 데이터 조회 실패: ...",
    "retry_hint": "네트워크 연결을 확인하거나 심볼을 다시 확인해주세요."
}
```

### 2. FinancialNewsTool

#### 입력
```json
{
    "query": "검색 쿼리 (예: AAPL earnings)",
    "max_results": 5
}
```

#### 출력
```json
{
    "status": "success",
    "query": "AAPL earnings",
    "results": [
        {
            "title": "Apple Reports Strong Q3 Earnings",
            "url": "https://example.com/news1",
            "snippet": "Apple Inc. reported better-than-expected earnings...",
            "published_date": "N/A"
        }
    ],
    "total_results": 3
}
```

#### 에러 응답
```json
{
    "status": "error",
    "error": "Tavily API 키가 설정되지 않았습니다.",
    "retry_hint": "API 키를 설정해주세요."
}
```

### 3. CalculatorTool

#### 입력
```json
{
    "expression": "계산식 문자열 (예: 2 + 3 * 4)"
}
```

#### 출력
```json
{
    "status": "success",
    "result": 14.0,
    "expression": "2 + 3 * 4"
}
```

#### 에러 응답
```json
{
    "status": "error",
    "error": "0으로 나눌 수 없습니다.",
    "expression": "10/0",
    "retry_hint": "계산식을 확인해주세요."
}
```

## 실행 파이프라인

### 워크플로우 실행 순서

#### 1. 초기화 단계
```python
initial_state = {
    "messages": [{"role": "user", "content": user_query}],
    "stock_symbol": "AAPL",
    "user_query": "AAPL 주식 분석 요청",
    "iteration": 0,
    "max_iterations": 3,
    "status": "researching",
    "errors": [],
    "tool_history": []
}
```

#### 2. Research 단계
- **입력**: `FinancialAgentState` with `status: "researching"`
- **처리**: 
  1. StockDataTool 실행
  2. FinancialNewsTool 실행
  3. 결과 상태 업데이트
- **출력**: `stock_data`, `news_data` 업데이트, `status: "analyzing"`

#### 3. Analysis 단계
- **입력**: `FinancialAgentState` with collected data
- **처리**:
  1. LLM 호출하여 데이터 분석
  2. 기술적/기본적 분석 수행
- **출력**: `analysis` 필드 업데이트, `status: "recommending"`

#### 4. Recommendation 단계
- **입력**: `FinancialAgentState` with analysis results
- **처리**:
  1. CalculatorTool 사용 (필요시)
  2. LLM 호출하여 추천사항 생성
- **출력**: `recommendations` 업데이트, `status: "reviewing"`

#### 5. Review 단계
- **입력**: `FinancialAgentState` with all results
- **처리**:
  1. LLM 호출하여 최종 보고서 작성
- **출력**: `final_report` 업데이트, `status: "done"`

#### 6. 조건부 분기
```python
def should_continue(state):
    if state["iteration"] >= state["max_iterations"]:
        return "end"
    if len(critical_errors) >= 2:
        return "end"
    if state["status"] == "done":
        return "end"
    if not state.get("stock_data") or state["stock_data"]["status"] != "success":
        return "continue"  # 재시도
    return "end"
```

### 에러 처리 플로우

#### 도구 레벨 에러 처리
```python
try:
    result = tool.run(input_data)
    if result["status"] == "success":
        return result
    else:
        # 재시도 로직
        for attempt in range(max_retries):
            time.sleep(0.5 * (2 ** attempt))
            result = tool.run(input_data)
            if result["status"] == "success":
                return result
        return error_result
except Exception as e:
    # 로깅 및 에러 반환
    logger.error({"tool": tool.name, "error": str(e)})
    return {"status": "error", "error": str(e)}
```

#### 워크플로우 레벨 에러 처리
```python
try:
    result = workflow.run(initial_state)
    return result
except Exception as e:
    logger.error({"workflow": "error", "message": str(e)})
    return {
        "status": "error",
        "errors": [str(e)],
        "final_report": "워크플로우 실행 중 오류가 발생했습니다."
    }
```

### 상태 전이 다이어그램

```
[초기화] 
    ↓
[researching] ──▶ StockDataTool ──▶ 성공 ──▶ [analyzing]
    │                     │                  │
    └──▶ 실패 ──▶ 재시도 ──┘                  │
                                              ↓
[reviewing] ◀── [recommending] ◀── LLM 분석 ◀── [analyzing]
    │              │
    ├──▶ 최종 보고서 생성
    │
    └──▶ should_continue() ──▶ [done] 또는 재시도
```

### 로깅 형태

#### 구조화된 로그 예시
```json
{
    "timestamp": "2024-01-15T10:30:45Z",
    "level": "INFO",
    "tool": "stock_data_tool",
    "symbol": "AAPL",
    "status": "success",
    "attempt": 1,
    "latency_ms": 1250.5,
    "result_summary": "Price: $150.25, Change: +2.15"
}
```

#### 에러 로그 예시
```json
{
    "timestamp": "2024-01-15T10:30:45Z",
    "level": "ERROR",
    "tool": "financial_news_tool",
    "query": "AAPL earnings",
    "status": "error",
    "error": "API 키가 유효하지 않습니다",
    "attempt": 3,
    "latency_ms": 5000.0,
    "retry_hint": "API 키를 확인해주세요"
}
```
