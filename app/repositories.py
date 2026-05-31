from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import AnalysisResult, WatchlistItem


def normalize_symbol(symbol: str) -> str:
    return symbol.strip().upper()


class WatchlistRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[WatchlistItem]:
        return list(self.db.scalars(select(WatchlistItem).order_by(WatchlistItem.symbol)))

    def get(self, symbol: str) -> WatchlistItem | None:
        normalized = normalize_symbol(symbol)
        return self.db.scalar(select(WatchlistItem).where(WatchlistItem.symbol == normalized))

    def add(self, symbol: str) -> WatchlistItem:
        normalized = normalize_symbol(symbol)
        existing = self.get(normalized)
        if existing is not None:
            return existing

        item = WatchlistItem(symbol=normalized)
        self.db.add(item)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            existing = self.get(normalized)
            if existing is not None:
                return existing
            raise
        self.db.refresh(item)
        return item

    def delete(self, symbol: str) -> bool:
        item = self.get(symbol)
        if item is None:
            return False

        self.db.delete(item)
        self.db.commit()
        return True


class AnalysisRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_latest(self, symbol: str) -> AnalysisResult | None:
        normalized = normalize_symbol(symbol)
        statement = (
            select(AnalysisResult)
            .where(AnalysisResult.symbol == normalized)
            .order_by(AnalysisResult.analyzed_at.desc(), AnalysisResult.id.desc())
            .limit(1)
        )
        return self.db.scalar(statement)

    def save(
        self,
        *,
        symbol: str,
        overall_judgment: str,
        summary: str,
        data_timestamp: datetime | None = None,
        key_reasons: list[str] | None = None,
        risk_factors: list[str] | None = None,
        support_levels: dict[str, Any] | None = None,
        should_alert: bool = False,
        triggered_alerts: list[str] | None = None,
        alert_reason: str | None = None,
        raw_result: dict[str, Any] | None = None,
    ) -> AnalysisResult:
        result = AnalysisResult(
            symbol=normalize_symbol(symbol),
            data_timestamp=data_timestamp,
            overall_judgment=overall_judgment,
            summary=summary,
            key_reasons=key_reasons or [],
            risk_factors=risk_factors or [],
            support_levels=support_levels or {},
            should_alert=should_alert,
            triggered_alerts=triggered_alerts or [],
            alert_reason=alert_reason,
            raw_result=raw_result,
        )
        self.db.add(result)
        self.db.commit()
        self.db.refresh(result)
        return result
