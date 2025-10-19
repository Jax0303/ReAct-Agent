# 금융 ReAct 에이전트 (Financial ReAct Agent)

**Google Gemini 2.0 Flash**를 활용한 멀티 에이전트 금융 분석 시스템입니다. 주식 데이터 수집, 뉴스 분석, 투자 추천까지 전체 투자 분석 파이프라인을 자동화합니다.

## 📋 프로젝트 개요

본 프로젝트는 ReAct (Reasoning and Acting) 패러다임을 따라 4개의 전문 에이전트가 협업하여 종합적인 금융 분석을 수행합니다:

- **Research Agent**: 주식 데이터 및 뉴스 수집
- **Analysis Agent**: LLM을 활용한 데이터 분석
- **Recommendation Agent**: 투자 추천사항 생성  
- **Review Agent**: 최종 보고서 작성

## 🏗️ 아키텍처

```
사용자 질문 → Research → Analysis → Recommendation → Review → 최종 보고서
     ↑                                                           ↓
     └────────────────── 재시도/에러 처리 ←─────────────────────┘
```

### 주요 컴포넌트
- **LangGraph StateGraph**: 워크플로우 관리
- **TypedDict State**: 구조화된 상태 관리
- **3개 도구**: StockData, News, Calculator
- **에러 처리**: 지수 백오프 재시도, 조기 종료

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

#### 1. 기본 실행
```bash
python examples/run_example.py
```

#### 2. 대화형 모드
```bash
python examples/run_example.py --interactive
```

#### 3. 프로그래밍 방식
```python
from src.workflows.financial_workflow import FinancialWorkflow

workflow = FinancialWorkflow(
    google_ai_api_key="your_google_ai_key",
    tavily_api_key="your_tavily_key"
)

result = workflow.run({
    "stock_symbol": "AAPL",
    "user_query": "AAPL 주식 분석해줘",
    "max_iterations": 3
})
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
```

## 📁 프로젝트 구조

```
ReAct-Agent/
├── README.md                 # 프로젝트 개요
├── requirements.txt          # 의존성 목록
├── .env.example             # 환경 변수 예시
├── src/
│   ├── agents/              # 에이전트 모듈
│   │   └── financial_agents.py
│   ├── tools/               # 도구 모듈
│   │   ├── stock_tools.py
│   │   └── calculator_tool.py
│   ├── workflows/           # 워크플로우 모듈
│   │   ├── state.py
│   │   └── financial_workflow.py
│   └── utils/               # 유틸리티
│       └── config.py
├── tests/                   # 테스트 코드
│   ├── test_tools.py
│   ├── test_graph_flow.py
│   └── test_end_to_end.py
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

- [ ] **HITL (Human-in-the-Loop)**: 사용자 승인 노드 추가
- [ ] **캐싱 시스템**: 자주 요청되는 데이터 캐싱
- [ ] **레이트 리미팅**: API 호출 제한 관리
- [ ] **마이크로배치**: 여러 주식 동시 분석
- [ ] **스트리밍 로그**: 실시간 진행 상황 모니터링
- [ ] **포트폴리오 분석**: 여러 종목 비교 분석

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## ⚠️ 면책조항

본 시스템이 제공하는 주식 분석 및 투자 추천은 **참고용**이며, 실제 투자 결정에 대한 책임은 사용자에게 있습니다. 투자에 따른 손실에 대해 개발자는 일절 책임지지 않습니다.