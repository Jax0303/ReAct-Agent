# 금융 ReAct 에이전트 (Financial ReAct Agent)

**Google Gemini 2.0 Flash**를 활용한 멀티 에이전트 금융 분석 시스템입니다. 주식 데이터 수집, 뉴스 분석, 투자 추천까지 전체 투자 분석 파이프라인을 자동화합니다.

## 📋 프로젝트 개요

본 프로젝트는 ReAct (Reasoning and Acting) 패러다임을 따라 4개의 전문 에이전트가 협업하여 종합적인 금융 분석을 수행합니다:

- **Research Agent**: 주식 데이터 및 뉴스 수집 (데이터 정규화/요약 포함)
- **Analysis Agent**: LLM을 활용한 데이터 분석
- **Recommendation Agent**: 투자 추천사항 생성
- **Human Approval Agent**: HITL(Human-in-the-Loop) 사용자 승인
- **Review Agent**: 최종 보고서 작성

## 🏗️ 아키텍처

```
사용자 질문 → Research → Analysis → Recommendation → [Human Approval] → Review → 최종 보고서
     ↑              ↓           ↓              ↓             ↓ (승인/거부)      ↓
     │        (정규화/요약) (구조적 로그)  (조건부 라우팅)                       │
     └─────────────────────── 재시도/에러 처리 ←────────────────────────────────┘
```

### 주요 컴포넌트
- **LangGraph StateGraph**: 워크플로우 관리 및 스트리밍 모드 지원
- **TypedDict State**: 구조화된 상태 관리
- **3개 도구**: StockData, News, Calculator (재시도 로직 포함)
- **데이터 정규화**: 툴 결과를 요약/정규화하여 상태 저장
- **구조적 로깅**: JSON 형식의 구조적 로그로 관찰성 향상
- **HITL**: Human-in-the-Loop 승인 프로세스
- **조건부 라우팅**: 승인/거부, 재시도 등 지능형 워크플로우 제어
- **에러 처리**: 지수 백오프 재시도, 조기 종료, 툴 실패 대응

## 🚀 설치 및 실행

### 전제 조건
- Python 3.8+
- **Google AI Studio API 키** (Gemini 2.0 Flash 사용)
- Tavily API 키 (뉴스 검색용, 선택사항)

### 설치 과정

1. **저장소 클론**
```bash
git clone <repository-url>
cd ReAct-Agent
```

2. **가상환경 설정**
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

3. **의존성 설치**
```bash
pip install -r requirements.txt
```

4. **환경 변수 설정**
```bash
cp .env.example .env
# .env 파일을 편집하여 API 키 설정
```

`.env` 파일 예시:
```env
GOOGLE_AI_API_KEY=your_google_ai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

**Google AI Studio API 키 발급:**
1. [Google AI Studio](https://aistudio.google.com/app/apikey) 방문
2. "Get API Key" 클릭
3. 프로젝트 선택 또는 새 프로젝트 생성
4. API 키 복사하여 `.env` 파일에 설정

### 실행 방법

#### 1. 메인 실행 파일 (대화형 모드)
```bash
python src/main.py
```

#### 2. 특정 주식 분석 (명령줄)
```bash
python src/main.py AAPL
```

#### 3. 스트리밍 모드 (실시간 로그)
```bash
python src/main.py AAPL stream
```

#### 4. 예제 스크립트
```bash
python examples/run_example.py
```

#### 5. 대화형 모드 (예제)
```bash
python examples/run_example.py --interactive
```

#### 6. 프로그래밍 방식
```python
from src.workflows.financial_workflow import FinancialWorkflow

workflow = FinancialWorkflow(
    google_ai_api_key="your_google_ai_key",
    tavily_api_key="your_tavily_key"
)

# 일반 실행
result = workflow.run({
    "stock_symbol": "AAPL",
    "user_query": "AAPL 주식 분석해줘",
    "max_iterations": 3
})

# 스트리밍 실행
for event in workflow.stream({
    "stock_symbol": "AAPL",
    "user_query": "AAPL 주식 분석해줘"
}):
    print(f"노드: {event['node']}, 상태: {event['status']}")
```

#### 7. 자동 승인 모드 (HITL 비활성화)
```bash
export AUTO_APPROVE=true
python src/main.py AAPL
```

## 📖 사용 예시

### 입력 예시
```
주식 심볼: AAPL
질문: AAPL 주식에 대한 투자 분석과 추천을 해주세요.
```

### 출력 예시
```
=== 분석 결과 ===
최종 상태: done
반복 횟수: 2

=== 최종 보고서 ===
1. Executive Summary
Apple Inc. (AAPL)는 현재 강력한 재무 상태를 보이고 있으며...

2. 주식 개요 및 현재 상황
- 현재 가격: $150.25
- 52주 고점: $182.94
- 시가총액: $2.5T
...

3. 핵심 분석 내용
- 기술적 분석: 상승 추세 유지
- 기본적 분석: 강력한 밸런스 시트
...

4. 투자 추천사항
- 추천: 보유/매수
- 목표가: $165 (10% 상승 여력)
...
```

## 🧪 테스트

### 전체 테스트 실행
```bash
pytest -q
```

### 개별 테스트
```bash
# 도구 테스트
pytest tests/test_tools.py -v

# 그래프 플로우 테스트  
pytest tests/test_graph_flow.py -v

# 통합 테스트
pytest tests/test_end_to_end.py -v

# 툴 실패 케이스 테스트
pytest tests/test_tool_failures.py -v

# 조건부 라우팅 테스트
pytest tests/test_conditional_routing.py -v
```

### 테스트 커버리지
- ✅ 도구 단위 테스트 (성공/실패 케이스)
- ✅ 워크플로우 그래프 테스트
- ✅ End-to-End 통합 테스트
- ✅ 툴 실패 시나리오 (잘못된 입력, API 오류, 재시도 메커니즘)
- ✅ 조건부 라우팅 (승인/거부, 재시도, 최대 반복)

## 📁 프로젝트 구조

```
ReAct-Agent/
├── README.md                 # 프로젝트 개요
├── requirements.txt          # 의존성 목록
├── .env.example             # 환경 변수 예시
├── .gitignore               # Git 무시 파일
├── src/
│   ├── main.py              # 메인 실행 파일 (대화형/스트리밍 모드)
│   ├── agents/              # 에이전트 모듈
│   │   ├── financial_agents.py  # 4개 금융 에이전트
│   │   └── human_approval_agent.py  # HITL 승인 에이전트
│   ├── tools/               # 도구 모듈
│   │   ├── stock_tools.py       # 주식 데이터 & 뉴스 툴
│   │   └── calculator_tool.py   # 계산기 툴
│   ├── workflows/           # 워크플로우 모듈
│   │   ├── state.py             # 상태 정의
│   │   └── financial_workflow.py  # 워크플로우 (조건부 라우팅)
│   └── utils/               # 유틸리티
│       ├── config.py            # 설정 관리
│       └── data_normalizer.py   # 데이터 정규화/요약
├── tests/                   # 테스트 코드
│   ├── test_tools.py            # 도구 단위 테스트
│   ├── test_graph_flow.py       # 워크플로우 그래프 테스트
│   ├── test_end_to_end.py       # 통합 테스트
│   ├── test_tool_failures.py    # 툴 실패 케이스
│   └── test_conditional_routing.py  # 조건부 라우팅
├── docs/                    # 문서
│   ├── architecture.md
│   └── api.md
└── examples/                # 실행 예제
    └── run_example.py
```

## 🎯 주요 설계 결정

### LangGraph 선택 이유
- **상태 관리**: TypedDict와 Annotated를 통한 강타입 상태 관리
- **조건부 분기**: 복잡한 에러 처리 및 재시도 로직 구현 가능
- **시각화**: 워크플로우의 명확한 시각화 및 디버깅 지원

### 멀티 에이전트 아키텍처
- **역할 분담**: 각 에이전트가 특정 전문 영역 담당
- **확장성**: 새로운 에이전트 추가 용이
- **유지보수**: 각 에이전트의 독립적 개발 및 테스트 가능

### 데이터 정규화 및 요약
- **목적**: 툴의 원시(raw) 데이터를 깔끔하게 정리하여 상태에 저장
- **기능**:
  - 주식 데이터: 가격 요약, 밸류에이션 평가, 52주 범위 내 위치 계산
  - 뉴스 데이터: 감성 분석, 전체 감성 평가, 뉴스 개요 생성
  - 계산 결과: 포맷팅 및 타임스탬프 추가
- **이점**: 에이전트가 처리하기 쉬운 구조화된 데이터 제공

### 구조적 로깅 (Observability)
- **형식**: JSON 기반 구조적 로그
- **내용**: 에이전트명, 액션, 상태, 타임스탬프, 주요 메트릭
- **장점**:
  - 로그 파싱 및 분석 용이
  - 디버깅 및 모니터링 향상
  - 프로덕션 환경에서의 추적성 확보

### HITL (Human-in-the-Loop)
- **목적**: 중요한 결정에 사용자 승인 필요
- **위치**: Recommendation 후, Review 전
- **동작**:
  - 분석 결과 요약 표시
  - 사용자 승인/거부 입력 받기
  - 승인 시 Review로 진행, 거부 시 워크플로우 종료
- **자동 승인 모드**: `AUTO_APPROVE=true` 환경 변수 설정

### 조건부 라우팅
- **승인 체크**: 사용자 승인/거부에 따라 워크플로우 경로 결정
- **재시도 로직**: 데이터 누락 시 Research 단계로 재시도
- **최대 반복 체크**: 무한 루프 방지
- **치명적 오류 감지**: 네트워크/API 오류 시 조기 종료

### 툴 실패 처리
- **지수 백오프 재시도**: 1초, 2초, 4초 간격으로 최대 3회 재시도
- **우아한 실패**: 툴 실패 시에도 워크플로우 계속 진행
- **오류 로깅**: 모든 실패 케이스 구조적 로그로 기록
- **폴백 메커니즘**: LLM 실패 시 기본 분석 제공

### LLM 및 도구 선택
- **LLM**: Google Gemini 2.0 Flash
  - 무료 할당량 충분 (OpenAI 대비)
  - 뛰어난 분석 품질
  - 빠른 응답 속도
  - Forward P/E, P/B, D/E 등 심화 재무 지표 분석
- **StockDataTool**: yfinance - 무료, 실시간 가격 데이터
- **NewsTool**: Tavily - 고품질 뉴스 검색 API
- **CalculatorTool**: 안전한 수학 계산

## ⚠️ 제한사항

1. **API 의존성**: 외부 API 서비스에 의존 (Google Gemini, Tavily, yfinance)
2. **실시간성**: 데이터 수집의 지연 가능성
3. **언어 지원**: 주로 한국어/영어 지원
4. **단일 종목**: 포트폴리오 분석 미지원
5. **법적 고지**: 투자 조언이 아닌 참고용 정보

## 🚧 향후 개선 계획

- [x] **HITL (Human-in-the-Loop)**: 사용자 승인 노드 추가 ✅
- [x] **스트리밍 로그**: 실시간 진행 상황 모니터링 ✅
- [x] **데이터 정규화**: 툴 결과 요약/정규화 ✅
- [x] **구조적 로깅**: JSON 기반 관찰성 향상 ✅
- [x] **조건부 라우팅**: 승인/거부 및 재시도 로직 ✅
- [x] **툴 실패 처리**: 실패 케이스 및 재시도 테스트 ✅
- [ ] **캐싱 시스템**: 자주 요청되는 데이터 캐싱
- [ ] **레이트 리미팅**: API 호출 제한 관리
- [ ] **마이크로배치**: 여러 주식 동시 분석
- [ ] **포트폴리오 분석**: 여러 종목 비교 분석
- [ ] **대시보드**: 웹 기반 실시간 모니터링 UI

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## ⚠️ 면책조항

본 시스템이 제공하는 주식 분석 및 투자 추천은 **참고용**이며, 실제 투자 결정에 대한 책임은 사용자에게 있습니다. 투자에 따른 손실에 대해 개발자는 일절 책임지지 않습니다.