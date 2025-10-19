# Architecture Documentation

## 시스템 아키텍처 개요

본 프로젝트는 LangGraph를 기반으로 한 금융 관련 ReAct 에이전트 시스템입니다. 다중 에이전트 아키텍처를 통해 주식 분석, 뉴스 수집, 추천 생성의 전체 생명주기를 관리합니다.

## 컴포넌트 다이어그램

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Research      │    │   Analysis      │    │ Recommendation  │
│    Agent        │───▶│    Agent        │───▶│    Agent        │
│                 │    │                 │    │                 │
│ - 주식 데이터   │    │ - LLM 분석      │    │ - 투자 추천     │
│ - 뉴스 수집     │    │ - 데이터 통합   │    │ - 리스크 평가   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Financial Workflow                           │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────┐ │
│  │   Tools     │  │   State     │  │Conditional  │  │ Review   │ │
│  │             │  │ Management  │  │   Edges     │  │ Agent    │ │
│  │- Stock Tool │  │             │  │             │  │          │ │
│  │- News Tool  │  │- TypedDict  │  │- 재시도     │  │- 최종    │ │
│  │- Calculator │  │- Annotated  │  │- 조기종료   │  │  보고서  │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └──────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## State 스키마

### FinancialAgentState

```python
class FinancialAgentState(TypedDict):
    # 대화 및 로깅
    messages: Annotated[List[Dict[str, str]], operator.add]
    errors: Annotated[List[str], operator.add]
    tool_history: Annotated[List[Dict], operator.add]
    
    # 분석 대상
    stock_symbol: str
    user_query: str
    
    # 수집된 데이터
    stock_data: Optional[Dict]
    market_data: Optional[Dict]
    news_data: Optional[List[Dict]]
    
    # 분석 결과
    analysis: Optional[str]
    recommendations: Optional[List[str]]
    final_report: str
    
    # 제어 변수
    iteration: int
    max_iterations: int
    status: str  # researching/analyzing/recommending/reviewing/done
```

### Reducers 설명

- `operator.add`: 리스트 타입의 필드들에 대해 새로운 항목을 추가하는 방식으로 상태를 관리합니다.
- `messages`, `errors`, `tool_history` 필드는 누적 방식으로 업데이트됩니다.

## 에이전트 역할 분담

### 1. ResearchAgent
- **역할**: 외부 데이터 수집
- **주요 기능**:
  - 주식 데이터 조회 (yfinance API)
  - 금융 뉴스 수집 (Tavily API)
  - 데이터 검증 및 정규화

### 2. AnalysisAgent
- **역할**: 데이터 분석 및 해석
- **주요 기능**:
  - LLM을 활용한 종합 분석
  - 기술적/기본적 분석 수행
  - 트렌드 파악 및 인사이트 도출

### 3. RecommendationAgent
- **역할**: 투자 추천 생성
- **주요 기능**:
  - 분석 결과 기반 추천사항 생성
  - 리스크 평가 및 주의사항 제공
  - 계산기 도구를 활용한 정량적 분석

### 4. ReviewAgent
- **역할**: 최종 보고서 작성
- **주요 기능**:
  - 모든 결과를 통합한 최종 보고서 생성
  - 사용자 친화적 형태로 결과 제공

## 그래프 구조 및 조건부 엣지

### 워크플로우 순서
1. **research** → **analyze** → **recommend** → **review**

### 조건부 엣지
- `should_continue` 함수가 다음을 결정:
  - 최대 반복 횟수 도달 여부
  - 심각한 에러 발생 여부
  - 데이터 수집 성공 여부
  - 완료 상태 도달 여부

### 재시도 로직
- 데이터 수집 실패 시 `research` 노드로 복귀
- 최대 반복 횟수 내에서만 재시도 허용

## 에러 처리 및 재시도 정책

### 도구 레벨
- **재시도 대상**: 네트워크 오류, 5xx 서버 에러, 타임아웃
- **재시도 안함**: 4xx 클라이언트 에러, 잘못된 입력
- **백오프 전략**: 지수 백오프 (0.5s → 1s → 2s)
- **최대 재시도**: 3회

### 워크플로우 레벨
- `should_continue` 함수로 전체 플로우 제어
- 심각한 에러 발생 시 조기 종료
- 최대 반복 횟수 제한으로 무한 루프 방지

### 로깅 정책
- 구조화된 로깅 (JSON 형태)
- 각 도구 사용 시 다음 정보 기록:
  - `status`: 성공/실패 상태
  - `error`: 에러 메시지 (실패 시)
  - `attempt`: 시도 횟수
  - `latency_ms`: 응답 시간

## 제한사항 및 개선 계획

### 현재 제한사항
1. **API 의존성**: 외부 API (OpenAI, Tavily, yfinance)에 대한 의존
2. **실시간 데이터**: 실시간 데이터 수집의 제한
3. **다국어 지원**: 한국어/영어 중심의 분석
4. **포트폴리오 분석**: 단일 주식 분석에 집중

### 미래 개선 계획
1. **HITL (Human-in-the-Loop)**: 사용자 승인 노드 추가
2. **캐싱**: 자주 요청되는 데이터 캐싱
3. **레이트 리미팅**: API 호출 제한 관리
4. **마이크로배치**: 여러 주식 동시 분석
5. **스트리밍 로그**: 실시간 프로세스 모니터링
