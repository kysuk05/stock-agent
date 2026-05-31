from __future__ import annotations

from app.repositories import AnalysisRepository


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_watchlist_crud(client):
    create_response = client.post("/watchlist", json={"symbol": " msft "})

    assert create_response.status_code == 201
    assert create_response.json()["symbol"] == "MSFT"
    assert any(item["symbol"] == "MSFT" for item in client.get("/watchlist").json())

    delete_response = client.delete("/watchlist/MSFT")

    assert delete_response.status_code == 204
    assert not any(item["symbol"] == "MSFT" for item in client.get("/watchlist").json())


def test_latest_analysis_returns_cached_result_without_external_calls(client, db_session, market_data, agent):
    AnalysisRepository(db_session).save(
        symbol="005930.KS",
        overall_judgment="neutral",
        summary="cached result",
        key_reasons=["cached reason"],
        risk_factors=[],
        support_levels={"latest_close": 72000},
        should_alert=False,
        triggered_alerts=[],
        alert_reason="No alert condition matched.",
        raw_result={"summary": "cached result"},
    )

    response = client.get("/stocks/005930.KS/analysis/latest")

    assert response.status_code == 200
    body = response.json()
    assert body["symbol"] == "005930.KS"
    assert body["summary"] == "cached result"
    assert body["raw_result"] == {"summary": "cached result"}
    assert market_data.calls == []
    assert agent.calls == []


def test_latest_analysis_cache_miss_uses_fake_market_data_and_agent(client, db_session, market_data, agent):
    response = client.get("/stocks/005930.KS/analysis/latest")

    assert response.status_code == 200
    body = response.json()
    assert body["symbol"] == "005930.KS"
    assert body["overall_judgment"] == "neutral"
    assert body["summary"] == "steady"
    assert body["raw_result"]["summary"] == "steady"
    assert market_data.calls == ["005930.KS"]
    assert [call.symbol for call in agent.calls] == ["005930.KS"]
    assert AnalysisRepository(db_session).get_latest("005930.KS").summary == "steady"


def test_latest_analysis_market_data_empty_returns_error(client, market_data, market_data_empty_error):
    market_data.error = market_data_empty_error

    response = client.get("/stocks/005930.KS/analysis/latest")

    assert response.status_code == 502
    assert "no market data" in response.json()["detail"]


def test_latest_analysis_agent_failure_returns_error(client, agent, agent_failure_error):
    agent.error = agent_failure_error

    response = client.get("/stocks/005930.KS/analysis/latest")

    assert response.status_code == 502
    assert "Gemini analysis request failed" in response.json()["detail"]


def test_index_page_response(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert 'value="005930.KS"' in response.text
    assert "/stocks/" in response.text
