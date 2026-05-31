from __future__ import annotations

from typing import Protocol

from fastapi import Depends
from sqlalchemy.orm import Session

from app.agent import AnalysisAgent, GeminiAnalysisAgent
from app.database import get_db
from app.market_data import MarketDataProvider, YFinanceMarketDataProvider
from app.models import AnalysisResult as StoredAnalysisResult
from app.repositories import AnalysisRepository, normalize_symbol
from app.schemas import model_to_dict


class AnalysisProvider(Protocol):
    def get_latest_analysis(self, symbol: str) -> StoredAnalysisResult:
        """Return the latest stored analysis, creating one when none exists."""


class AnalysisService:
    def __init__(
        self,
        *,
        analysis_repository: AnalysisRepository,
        market_data_provider: MarketDataProvider,
        agent: AnalysisAgent,
    ) -> None:
        self.analysis_repository = analysis_repository
        self.market_data_provider = market_data_provider
        self.agent = agent

    def get_latest_analysis(self, symbol: str) -> StoredAnalysisResult:
        normalized_symbol = normalize_symbol(symbol)
        if not normalized_symbol:
            raise ValueError("symbol is required")

        latest = self.analysis_repository.get_latest(normalized_symbol)
        if latest is not None:
            return latest

        market_data = self.market_data_provider.fetch(normalized_symbol)
        agent_result = self.agent.analyze(market_data)
        raw_result = model_to_dict(agent_result)

        return self.analysis_repository.save(
            symbol=agent_result.symbol,
            data_timestamp=agent_result.data_time,
            overall_judgment=agent_result.verdict,
            summary=agent_result.summary,
            key_reasons=agent_result.key_reasons,
            risk_factors=agent_result.risk_factors,
            support_levels=agent_result.indicators,
            should_alert=agent_result.alert_triggered,
            triggered_alerts=agent_result.matched_alert_conditions,
            alert_reason=agent_result.alert_reason,
            raw_result=raw_result,
        )


def get_market_data_provider() -> MarketDataProvider:
    return YFinanceMarketDataProvider()


def get_analysis_agent() -> AnalysisAgent:
    return GeminiAnalysisAgent()


def get_analysis_service(
    db: Session = Depends(get_db),
    market_data_provider: MarketDataProvider = Depends(get_market_data_provider),
    agent: AnalysisAgent = Depends(get_analysis_agent),
) -> AnalysisProvider:
    return AnalysisService(
        analysis_repository=AnalysisRepository(db),
        market_data_provider=market_data_provider,
        agent=agent,
    )
