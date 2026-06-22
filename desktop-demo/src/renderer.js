const stockData = [
  {
    symbol: "005930.KS",
    name: "삼성전자",
    avatar: "삼성",
    price: 74800,
    change: 2.18,
    volumeRatio: "1.8x",
    support: "72,500",
    alert: "조건 충족",
    dataTime: "13:58",
    analyses: [
      {
        id: 101,
        time: "06.22 · 14:00",
        verdict: "상승",
        summary: "반도체 업황 회복 기대와 외국인 수급이 단기 흐름을 지지합니다.",
        reasons: ["20일 평균 대비 거래량 1.8배 증가", "5일 이동평균선이 20일선을 상향 돌파", "외국인 순매수 흐름 3거래일 연속"],
        risks: ["단기 상승에 따른 차익 실현 가능성", "원/달러 환율 변동성 확대", "메모리 가격 회복 속도 불확실성"]
      },
      { id: 102, time: "06.22 · 13:00", verdict: "중립", summary: "방향성 확인 전까지 주요 지지선 관찰이 필요합니다.", reasons: ["단기 이동평균선 부근 횡보", "외국인 수급은 소폭 개선", "거래량은 평균 수준 유지"], risks: ["상단 매물대 저항", "환율 민감도", "추가 거래량 확인 필요"] },
      { id: 103, time: "06.22 · 12:00", verdict: "관망", summary: "거래량 둔화로 추가 확인이 필요한 구간입니다.", reasons: ["주요 지지선 위 가격 유지", "기관 매도 규모 감소", "낙폭 일부 회복"], risks: ["거래량 둔화", "단기 추세 미확정", "시장 변동성 확대"] }
    ]
  },
  {
    symbol: "000660.KS",
    name: "SK하이닉스",
    avatar: "SK",
    price: 189400,
    change: 1.04,
    volumeRatio: "1.4x",
    support: "184,000",
    alert: "대기",
    dataTime: "13:57",
    analyses: [
      { id: 201, time: "06.22 · 14:00", verdict: "상승", summary: "HBM 수요 기대가 유지되며 단기 수급도 양호합니다.", reasons: ["외국인 순매수 전환", "고점 돌파 시도", "반도체 업종 강세"], risks: ["최근 상승폭 부담", "업종 변동성", "실적 기대 선반영"] },
      { id: 202, time: "06.22 · 13:00", verdict: "중립", summary: "상승 추세 안에서 단기 숨 고르기가 나타납니다.", reasons: ["20일선 상단 유지", "거래량 안정", "업종 흐름 양호"], risks: ["고점 매물", "단기 과열", "환율 변화"] }
    ]
  },
  {
    symbol: "035420.KS",
    name: "NAVER",
    avatar: "N",
    price: 214500,
    change: -0.46,
    volumeRatio: "0.9x",
    support: "210,000",
    alert: "조건 미충족",
    dataTime: "13:56",
    analyses: [
      { id: 301, time: "06.22 · 14:00", verdict: "중립", summary: "가격은 지지선 위에 있으나 거래량 확인이 필요합니다.", reasons: ["210,000원 지지", "기관 수급 개선", "낙폭 제한"], risks: ["거래량 평균 하회", "성장주 변동성", "단기 방향성 부재"] },
      { id: 302, time: "06.22 · 13:00", verdict: "관망", summary: "명확한 수급 신호가 없어 관찰이 필요한 구간입니다.", reasons: ["지지선 근접", "매도 압력 완화", "업종 보합"], risks: ["수급 공백", "저항선 미돌파", "시장 민감도"] }
    ]
  },
  {
    symbol: "005380.KS",
    name: "현대차",
    avatar: "현대",
    price: 281000,
    change: 0.72,
    volumeRatio: "1.2x",
    support: "276,000",
    alert: "대기",
    dataTime: "13:55",
    analyses: [
      { id: 401, time: "06.22 · 14:00", verdict: "상승", summary: "실적 기대와 안정적인 수급이 완만한 상승을 지지합니다.", reasons: ["기관 순매수", "주요 이동평균선 상단", "거래량 점진적 증가"], risks: ["환율 변동", "자동차 수요 둔화", "단기 저항선 근접"] },
      { id: 402, time: "06.22 · 13:00", verdict: "중립", summary: "추세는 유지되지만 저항선 확인이 필요합니다.", reasons: ["지지선 유지", "기관 수급 양호", "낙폭 제한"], risks: ["상단 매물", "환율 민감도", "거래량 부족"] }
    ]
  }
];

let selectedSymbol = stockData[0].symbol;
let selectedAnalysisId = stockData[0].analyses[0].id;
let toastTimer;

const formatPrice = (value) => new Intl.NumberFormat("ko-KR").format(value);
const currentStock = () => stockData.find((stock) => stock.symbol === selectedSymbol);
const currentAnalysis = () => currentStock().analyses.find((item) => item.id === selectedAnalysisId) || currentStock().analyses[0];

function verdictClass(verdict) {
  if (verdict === "상승") return "verdict-up";
  if (verdict === "중립") return "verdict-neutral";
  return "verdict-watch";
}

function showToast(message) {
  const toast = document.querySelector("#toast");
  toast.textContent = message;
  toast.classList.add("show");
  window.clearTimeout(toastTimer);
  toastTimer = window.setTimeout(() => toast.classList.remove("show"), 2200);
}

function renderWatchlist() {
  const list = document.querySelector("#watchlist");
  list.innerHTML = "";
  stockData.forEach((stock) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `watchlist-item${stock.symbol === selectedSymbol ? " active" : ""}`;
    const sign = stock.change >= 0 ? "+" : "";
    button.innerHTML = `
      <span class="stock-avatar">${stock.avatar}</span>
      <span class="stock-label"><strong>${stock.name}</strong><small>${stock.symbol}</small></span>
      <span class="stock-price"><strong>${formatPrice(stock.price)}</strong><em class="${stock.change >= 0 ? "positive" : "negative"}">${sign}${stock.change.toFixed(2)}%</em></span>
    `;
    button.addEventListener("click", () => selectStock(stock.symbol));
    list.appendChild(button);
  });
  document.querySelector("#watchlist-count").textContent = `${stockData.length} ITEMS`;
}

function renderAnalysis() {
  const stock = currentStock();
  const analysis = currentAnalysis();
  const verdict = document.querySelector("#verdict");
  const sign = stock.change >= 0 ? "+" : "";

  document.querySelector("#analysis-time").textContent = `${analysis.id === stock.analyses[0].id ? "LATEST ANALYSIS" : "HISTORY ANALYSIS"} · ${analysis.time} KST`;
  verdict.textContent = analysis.verdict;
  verdict.className = `verdict ${verdictClass(analysis.verdict)}`;
  document.querySelector("#hero-symbol-name").textContent = stock.name;
  document.querySelector("#analysis-summary").textContent = analysis.summary;
  document.querySelector("#current-price").textContent = formatPrice(stock.price);
  document.querySelector("#price-change").textContent = `${stock.change >= 0 ? "▲" : "▼"} ${sign}${stock.change.toFixed(2)}%`;
  document.querySelector("#price-change").className = stock.change >= 0 ? "positive" : "negative";
  document.querySelector("#volume-ratio").textContent = stock.volumeRatio;
  document.querySelector("#support-price").textContent = stock.support;
  document.querySelector("#alert-status").textContent = stock.alert;
  document.querySelector("#data-time").textContent = stock.dataTime;
  renderList("#reason-list", analysis.reasons);
  renderList("#risk-list", analysis.risks);
  renderHistory();
}

function renderList(selector, items) {
  const list = document.querySelector(selector);
  list.innerHTML = items.map((item) => `<li>${item}</li>`).join("");
}

function renderHistory() {
  const stock = currentStock();
  const list = document.querySelector("#history-list");
  list.innerHTML = "";
  stock.analyses.forEach((analysis) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `history-item${analysis.id === selectedAnalysisId ? " active" : ""}`;
    button.innerHTML = `
      <span class="history-time">${analysis.time}</span>
      <span class="history-verdict">${analysis.verdict}</span>
      <span class="history-summary">${analysis.summary}</span>
      <span class="history-arrow">›</span>
    `;
    button.addEventListener("click", () => {
      selectedAnalysisId = analysis.id;
      renderAnalysis();
      showToast(`${analysis.time} 분석을 표시합니다.`);
    });
    list.appendChild(button);
  });
}

function selectStock(symbol) {
  selectedSymbol = symbol;
  selectedAnalysisId = currentStock().analyses[0].id;
  renderWatchlist();
  renderAnalysis();
  showToast(`${currentStock().name} mock 데이터를 불러왔습니다.`);
}

document.querySelector("#search-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const query = document.querySelector("#search-input").value.trim().toLowerCase();
  const match = stockData.find((stock) => stock.name.toLowerCase().includes(query) || stock.symbol.toLowerCase().includes(query));
  if (!query || !match) {
    showToast("데모 관심종목에서 검색 결과를 찾지 못했습니다.");
    return;
  }
  selectStock(match.symbol);
  document.querySelector("#search-input").value = "";
});

document.querySelector("#add-symbol-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const input = document.querySelector("#add-symbol-input");
  const name = input.value.trim();
  if (!name) {
    showToast("추가할 종목명을 입력하세요.");
    return;
  }
  const id = 500 + stockData.length;
  stockData.push({
    symbol: `DEMO${stockData.length + 1}.KS`, name, avatar: name.slice(0, 2), price: 100000, change: 0,
    volumeRatio: "1.0x", support: "98,000", alert: "조건 미충족", dataTime: "14:00",
    analyses: [{ id, time: "06.22 · 14:00", verdict: "중립", summary: "새로 추가한 데모 종목의 mock 분석입니다.", reasons: ["관심종목 추가 동작 확인", "고정된 데모 시세 사용", "API 연동 전 UI 상태"], risks: ["실제 시세 아님", "AI 분석 아님", "앱 재시작 시 초기화"] }]
  });
  input.value = "";
  selectStock(`DEMO${stockData.length}.KS`);
});

document.querySelector("#latest-button").addEventListener("click", () => {
  selectedAnalysisId = currentStock().analyses[0].id;
  renderAnalysis();
  showToast("최신 mock 분석으로 돌아왔습니다.");
});

document.querySelector("#refresh-button").addEventListener("click", (event) => {
  event.currentTarget.classList.add("spinning");
  currentStock().dataTime = new Date().toLocaleTimeString("ko-KR", { hour: "2-digit", minute: "2-digit", hour12: false });
  window.setTimeout(() => event.currentTarget.classList.remove("spinning"), 650);
  renderAnalysis();
  showToast("mock 데이터의 갱신 시각을 업데이트했습니다.");
});

document.querySelectorAll(".nav-item").forEach((item) => {
  item.addEventListener("click", () => {
    if (item.dataset.view === "대시보드") return;
    showToast(`${item.dataset.view} 화면은 후속 데모 범위입니다.`);
  });
});

renderWatchlist();
renderAnalysis();
