# 데모 스크린샷 가이드

## 📸 추천 스크린샷 3장 + 1장(보너스)

### 1️⃣ 전체 워크플로우 실행 (필수)

**명령어:**
```bash
cd /home/user/ReAct-Agent
export PYTHONPATH=/home/user/ReAct-Agent:$PYTHONPATH
export AUTO_APPROVE=true
python3 src/main.py AAPL 2>&1 | grep -v "^E0000\|^W0000\|^2025-"
```

**캡처할 부분:**
- 환영 메시지 (🚀 ReAct 금융 분석 에이전트)
- 분석 결과 요약 섹션:
  - 📈 주식 정보 (심볼, 현재가, 변동, 추세, PER)
  - 📰 뉴스 정보 (개수, 감성, 분포)
  - 💡 투자 추천사항 (상위 5개)
  - 📝 최종 보고서 (미리보기)

**강조할 내용:**
- ✅ 실시간 데이터 수집
- ✅ AI 기반 분석 (Google Gemini)
- ✅ 데이터 정규화 (추세 판단, 감성 분석)
- ✅ 종합 투자 보고서

---

### 2️⃣ 구조적 로깅 + HITL 승인 (필수)

**명령어:**
```bash
cd /home/user/ReAct-Agent
export PYTHONPATH=/home/user/ReAct-Agent:$PYTHONPATH
export AUTO_APPROVE=true
python3 src/main.py TSLA 2>&1 | grep -E "INFO|agent|normalizer|HumanApproval" | head -50
```

**캡처할 부분:**
- JSON 구조적 로그 예시:
  ```json
  {
    "agent": "ResearchAgent",
    "action": "stock_data_collected",
    "symbol": "TSLA",
    "price": 439.31,
    "trend": "상승",
    "pe_evaluation": "고평가",
    "status": "success"
  }
  ```
- 데이터 정규화 로그:
  ```json
  {
    "normalizer": "stock_data",
    "symbol": "TSLA",
    "trend": "상승",
    "pe_evaluation": "고평가"
  }
  ```
- HITL 승인 로그:
  ```json
  {
    "agent": "HumanApprovalAgent",
    "action": "auto_approved",
    "reason": "AUTO_APPROVE environment variable is set"
  }
  ```

**강조할 내용:**
- ✅ JSON 구조적 로깅 (관찰성)
- ✅ 데이터 정규화 (추세, PER 평가)
- ✅ HITL 자동 승인
- ✅ 조건부 라우팅

---

### 3️⃣ 스트리밍 모드 (필수)

**명령어:**
```bash
cd /home/user/ReAct-Agent
export PYTHONPATH=/home/user/ReAct-Agent:$PYTHONPATH
export AUTO_APPROVE=true
python3 src/main.py NVDA stream 2>&1 | grep -E "^(🔍|📊|💡|✋|📝|✅)"
```

**캡처할 부분:**
- 실시간 노드 진행 상황:
  ```
  🔍 RESEARCH - analyzing
  📊 ANALYZE - recommending
  💡 RECOMMEND - reviewing
  ✋ HUMAN_APPROVAL - reviewing
  📝 REVIEW - done
  ✅ 스트리밍 분석 완료!
  ```

**강조할 내용:**
- ✅ 실시간 스트리밍 모드
- ✅ 노드별 상태 추적
- ✅ 이모지 시각화
- ✅ LangGraph stream() 통합

---

### 4️⃣ 테스트 결과 (보너스)

**명령어:**
```bash
cd /home/user/ReAct-Agent
python3 -m pytest tests/ -v --tb=line
```

**캡처할 부분:**
- 테스트 결과 요약:
  ```
  ======================== 25 passed, 1 skipped ========================
  
  tests/test_conditional_routing.py::... PASSED [  3%]
  tests/test_tool_failures.py::... PASSED [ 46%]
  tests/test_tools.py::... PASSED [ 76%]
  ```

**강조할 내용:**
- ✅ 96.2% 테스트 통과 (25/26)
- ✅ 조건부 라우팅 (7개)
- ✅ 툴 실패 처리 (8개)
- ✅ End-to-End (2개)

---

## 🎨 스크린샷 레이아웃 권장사항

### 스크린샷 1: 전체 워크플로우
```
┌─────────────────────────────────────────┐
│ 🚀 ReAct 금융 분석 에이전트          │
├─────────────────────────────────────────┤
│                                         │
│ 📊 분석 결과 요약                      │
│ ├─ 📈 주식 정보                        │
│ │  ├─ 심볼: AAPL                       │
│ │  ├─ 현재가: $252.29                  │
│ │  ├─ 추세: 📈 상승                    │
│ │  └─ PER: 38.34 (고평가)              │
│ │                                       │
│ ├─ 📰 뉴스 정보                        │
│ │  ├─ 개수: 3개                        │
│ │  ├─ 전체 감성: 📈 긍정적             │
│ │  └─ 긍정: 1, 중립: 2                 │
│ │                                       │
│ └─ 💡 투자 추천사항 (15개)             │
│    ├─ 1. 보유 포지션 유지              │
│    ├─ 2. 목표가: $270                  │
│    └─ 3. 리스크: 고평가 PER            │
└─────────────────────────────────────────┘
```

### 스크린샷 2: 구조적 로깅
```
┌─────────────────────────────────────────┐
│ JSON 구조적 로그                       │
├─────────────────────────────────────────┤
│                                         │
│ ResearchAgent:                          │
│ {                                       │
│   "agent": "ResearchAgent",             │
│   "action": "stock_data_collected",     │
│   "symbol": "TSLA",                     │
│   "price": 439.31,                      │
│   "trend": "상승",                      │
│   "status": "success"                   │
│ }                                       │
│                                         │
│ DataNormalizer:                         │
│ {                                       │
│   "normalizer": "stock_data",           │
│   "trend": "상승",                      │
│   "pe_evaluation": "고평가"             │
│ }                                       │
│                                         │
│ HumanApprovalAgent:                     │
│ {                                       │
│   "agent": "HumanApprovalAgent",        │
│   "action": "auto_approved"             │
│ }                                       │
└─────────────────────────────────────────┘
```

### 스크린샷 3: 스트리밍 모드
```
┌─────────────────────────────────────────┐
│ 실시간 스트리밍 진행 상황              │
├─────────────────────────────────────────┤
│                                         │
│ 🔍 RESEARCH - analyzing                 │
│ 📊 ANALYZE - recommending               │
│ 💡 RECOMMEND - reviewing                │
│ ✋ HUMAN_APPROVAL - reviewing           │
│ 📝 REVIEW - done                        │
│ ✅ 스트리밍 분석 완료!                  │
│                                         │
└─────────────────────────────────────────┘
```

---

## 💡 추가 팁

### 강조할 핵심 기능
1. **실용성**: 실제 주식 데이터로 작동
2. **자동화**: 전체 파이프라인 자동 실행
3. **AI 활용**: Google Gemini 2.0 Flash
4. **관찰성**: 구조적 로깅
5. **사용자 제어**: HITL 승인
6. **실시간**: 스트리밍 모드

### 설명에 포함할 내용
- "ReAct 패러다임 기반 멀티 에이전트 시스템"
- "Google Gemini 2.0 Flash를 활용한 AI 분석"
- "HITL, 데이터 정규화, 구조적 로깅 등 보너스 기능 구현"
- "96.2% 테스트 통과율로 검증된 견고성"

---

## 📝 스크린샷 설명 예시

### 스크린샷 1
> **전체 워크플로우 실행 결과**
> 
> AAPL(애플) 주식에 대한 실시간 데이터 수집, AI 기반 분석, 투자 추천사항 생성, 최종 보고서 작성까지 전체 파이프라인이 자동으로 실행됩니다. 데이터 정규화를 통해 추세(상승/하락), PER 평가(고평가/저평가), 뉴스 감성(긍정/부정/중립)을 자동으로 판단합니다.

### 스크린샷 2
> **구조적 로깅 및 HITL 승인**
> 
> JSON 형식의 구조적 로그로 모든 에이전트의 동작을 추적할 수 있습니다. 데이터 정규화(trend, pe_evaluation) 결과와 HITL(Human-in-the-Loop) 자동 승인 프로세스를 확인할 수 있습니다. 프로덕션 환경에서의 모니터링과 디버깅이 용이합니다.

### 스크린샷 3
> **실시간 스트리밍 모드**
> 
> LangGraph의 stream() 메서드를 활용하여 각 노드의 실행 상태를 실시간으로 모니터링할 수 있습니다. 이모지와 함께 시각화된 진행 상황으로 사용자 경험을 향상시켰습니다.

### 스크린샷 4 (보너스)
> **종합 테스트 결과**
> 
> 26개의 테스트 중 25개가 통과하여 96.2%의 성공률을 달성했습니다. 조건부 라우팅, 툴 실패 처리, End-to-End 통합 등 모든 핵심 기능이 검증되었습니다.

