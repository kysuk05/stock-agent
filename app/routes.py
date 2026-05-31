from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.agent import AgentConfigurationError, AnalysisAgentError
from app.database import get_db
from app.market_data import MarketDataError
from app.repositories import WatchlistRepository
from app.schemas import AnalysisResultRead, WatchlistCreate, WatchlistItemRead
from app.services import AnalysisProvider, get_analysis_service


router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {"default_symbol": "005930.KS"},
    )


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/watchlist", response_model=WatchlistItemRead, status_code=status.HTTP_201_CREATED)
def add_watchlist_item(payload: WatchlistCreate, db: Session = Depends(get_db)):
    return WatchlistRepository(db).add(payload.symbol)


@router.get("/watchlist", response_model=list[WatchlistItemRead])
def list_watchlist_items(db: Session = Depends(get_db)):
    return WatchlistRepository(db).list()


@router.delete("/watchlist/{symbol}", status_code=status.HTTP_204_NO_CONTENT)
def delete_watchlist_item(symbol: str, db: Session = Depends(get_db)):
    deleted = WatchlistRepository(db).delete(symbol)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="watchlist item not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/stocks/{symbol}/analysis/latest", response_model=AnalysisResultRead)
def get_latest_analysis(
    symbol: str,
    analysis_service: AnalysisProvider = Depends(get_analysis_service),
):
    try:
        result = analysis_service.get_latest_analysis(symbol)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except MarketDataError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    except (AnalysisAgentError, AgentConfigurationError) as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    return result
