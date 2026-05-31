# 분석시스템 v1 구현 및 데모 계획

## Summary

분석시스템부터 구현한다. 대시보드 앱은 만들지 않고, 대신 최신 분석결과만 조회할 수 있는 아주 단순한 웹 화면을 FastAPI 서버 안에 붙인다.

구현 결과물은 다음을 포함한다.

- FastAPI 분석시스템
- SQLite 저장소
- yfinance 기반 금융 데이터 조회
- Gemini API 기반 분석 agent
- 분석결과 JSON 저장
- 최신 분석결과 조회 API
- 간단한 분석결과 조회 화면
- 삼성전자 `005930.KS` 샘플 데모 실행

## Implementation Changes

### 프로젝트 부트스트랩

- Python FastAPI 프로젝트 구조를 생성한다.
- 의존성은 `fastapi`, `uvicorn`, `sqlalchemy`, `pydantic`, `yfinance`, `pytest`, `httpx`를 기준으로 둔다.
- Gemini API 호출은 신규 SDK 의존성을 추가하지 않고 `httpx` 기반 REST adapter로 구현한다.
- 환경변수는 `.env.example`로 문서화한다.
- `GEMINI_API_KEY`는 필수, `GEMINI_MODEL`은 선택이며 기본값은 `gemini-2.5-flash`로 둔다.

### 저장소 및 도메인

- SQLite를 사용한다.
- 관심종목 테이블과 분석결과 테이블을 만든다.
- 분석결과는 정규 필드와 `raw_result_json`을 함께 저장한다.
- 삼성전자 샘플을 위해 `005930.KS`를 관심종목으로 등록할 수 있게 한다.

### 분석 흐름

- `GET /stocks/{symbol}/analysis/latest`
  - 기존 분석결과가 있으면 즉시 반환한다.
  - 기존 분석결과가 없으면 yfinance로 데이터를 조회한다.
  - 조회 데이터와 시스템 프롬프트를 Gemini agent에 전달한다.
  - Structured Outputs/Pydantic 스키마로 분석결과 JSON을 받는다.
  - 결과를 SQLite에 저장한 뒤 반환한다.
- v1에서는 주기 실행 스케줄러와 알림 발송은 구현하지 않는다.

### 간단한 화면

- `GET /`
  - 종목 코드 입력 폼과 분석결과 표시 영역만 제공한다.
  - 기본 입력값은 `005930.KS`로 둔다.
- 화면은 분석결과 조회 API를 호출하거나 서버 렌더링으로 결과를 표시한다.
- 디자인은 최소화한다. 추후 대시보드 앱으로 교체될 임시 화면으로 간주한다.

## Test Plan

- `pytest` 전체 테스트가 성공해야 한다.
- 관심종목 등록/조회/삭제 API를 검증한다.
- 분석결과가 이미 있으면 yfinance/Gemini 호출 없이 저장된 결과를 반환하는지 검증한다.
- 분석결과가 없으면 데이터 조회, agent 분석, JSON 저장, API 반환까지 수행하는지 검증한다.
- yfinance 데이터가 비어 있으면 명확한 에러를 반환하는지 검증한다.
- Gemini 호출 실패 시 API 에러를 반환하는지 검증한다.
- 간단한 화면 `GET /`이 정상 응답하는지 검증한다.
- 외부 API 의존 테스트는 mock으로 처리한다.

## Demo Plan

- 구현 완료 후 FastAPI 서버를 실행한다.
- `http://localhost:8000`에 접속한다.
- 기본 종목 `005930.KS`로 최신 분석결과 조회를 실행한다.
- 분석결과가 없으면 실제 yfinance 데이터와 Gemini API를 사용해 최초 분석을 생성한다.
- 생성된 분석결과가 SQLite에 JSON으로 저장되고 화면에 표시되는지 확인한다.

## Assumptions

- 삼성전자는 yfinance 심볼 `005930.KS`를 사용한다.
- Gemini API 키는 실행 환경의 `GEMINI_API_KEY`에 존재해야 한다.
- 화면은 임시 조회 화면이며, 추후 별도 대시보드 앱으로 대체한다.
- 알림 발송, 주기 스케줄러, 복잡한 조건 빌더는 이번 구현에서 제외한다.
- 분석결과가 하나라도 있으면 최신 결과로 반환하고, 1시간 경과 재분석 정책은 나중에 추가한다.
