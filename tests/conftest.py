from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401
from app.agent import AnalysisAgentError
from app.database import Base, get_db
from app.main import app
from app.market_data import MarketDataError
from app.schemas import AnalysisResult, MarketDataSnapshot, MarketIndicators
from app.services import get_analysis_agent, get_market_data_provider


class FakeMarketDataProvider:
    def __init__(self, snapshot: MarketDataSnapshot | None = None, error: Exception | None = None) -> None:
        self.snapshot = snapshot or MarketDataSnapshot(
            symbol="005930.KS",
            data_time=datetime(2026, 5, 30, tzinfo=timezone.utc),
            records=[],
            indicators=MarketIndicators(latest_close=72000, latest_volume=1000),
        )
        self.error = error
        self.calls: list[str] = []

    def fetch(self, symbol: str) -> MarketDataSnapshot:
        self.calls.append(symbol)
        if self.error is not None:
            raise self.error
        return self.snapshot.model_copy(update={"symbol": symbol})


class FakeAnalysisAgent:
    def __init__(self, result: AnalysisResult | None = None, error: Exception | None = None) -> None:
        self.result = result
        self.error = error
        self.calls: list[MarketDataSnapshot] = []

    def analyze(self, market_data: MarketDataSnapshot, alert_conditions=None) -> AnalysisResult:
        self.calls.append(market_data)
        if self.error is not None:
            raise self.error
        return self.result or AnalysisResult(
            symbol=market_data.symbol,
            analysis_time=datetime(2026, 5, 30, 1, tzinfo=timezone.utc),
            data_time=market_data.data_time,
            verdict="neutral",
            summary="steady",
            key_reasons=["volume is normal"],
            risk_factors=["market-wide volatility"],
            indicators={"latest_close": market_data.indicators.latest_close},
            alert_triggered=False,
            matched_alert_conditions=[],
            alert_reason="No alert condition matched.",
        )


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def market_data() -> FakeMarketDataProvider:
    return FakeMarketDataProvider()


@pytest.fixture
def agent() -> FakeAnalysisAgent:
    return FakeAnalysisAgent()


@pytest.fixture
def client(db_session, market_data: FakeMarketDataProvider, agent: FakeAnalysisAgent) -> TestClient:
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_market_data_provider] = lambda: market_data
    app.dependency_overrides[get_analysis_agent] = lambda: agent
    test_client = TestClient(app)
    try:
        yield test_client
    finally:
        app.dependency_overrides.clear()
        test_client.close()


@pytest.fixture
def market_data_empty_error() -> MarketDataError:
    return MarketDataError("no market data returned for 005930.KS")


@pytest.fixture
def agent_failure_error() -> AnalysisAgentError:
    return AnalysisAgentError("Gemini analysis request failed")
