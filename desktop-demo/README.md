# Stock Agent Electron Demo

FastAPI나 외부 API에 연결하지 않고 Stock Agent의 데스크톱 UI와 사용자 흐름을 확인하는 Electron 데모입니다.

## Electron을 사용한 이유

- 기존 FastAPI 백엔드와 분리해서 데스크톱 화면만 빠르게 검증할 수 있습니다.
- HTML, CSS, JavaScript로 화면을 만들기 때문에 현재 웹 대시보드 구조와 지식을 재사용하기 쉽습니다.
- 나중에 로컬 실행 앱으로 포장할 때 Windows/macOS/Linux 배포 흐름을 비교적 단순하게 가져갈 수 있습니다.
- main process와 renderer process를 분리하면 API 키나 카카오 토큰 같은 민감 정보는 백엔드에 남기고, 화면은 안전한 preload 경계 안에서 다룰 수 있습니다.

## 요구사항

- Node.js 22.12 이상
- npm 10 이상

## 실행

```powershell
cd desktop-demo
npm install
npm start
```

Electron 42.4.1을 사용합니다. 저장소의 기존 Node.js 18 환경에서는 설치되지 않으므로 Node.js를 먼저 업그레이드해야 합니다.

## 정적 화면 확인

`src/index.html`은 브라우저로 직접 열어도 핵심 화면과 mock 상호작용을 확인할 수 있습니다.

## 포함된 동작

- 관심종목 선택 및 검색
- 데모 종목 추가
- 최신/과거 분석 전환
- mock 갱신 시각 변경
- 미구현 메뉴 안내 토스트

## 실제 연동에서 교체할 부분

`src/renderer.js`의 `stockData`와 상태 변경 함수를 FastAPI 호출로 교체합니다. Electron의 main process에는 API 키를 두지 않고, 인증 및 민감 정보는 백엔드가 관리하도록 유지합니다.
