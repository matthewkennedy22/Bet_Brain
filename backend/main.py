from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import List, Optional
import asyncio

from database import init_db, get_session
from models import Game, BetPick, NewsItem
from data_fetcher import OddsFetcher, NewsFetcher
from algorithm import BettingAlgorithm
from config import SPORTS

app = FastAPI(
    title="Sports Betting Analyzer",
    description="AI-powered betting picks and analysis",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

odds_fetcher = OddsFetcher()
news_fetcher = NewsFetcher()
algorithm = BettingAlgorithm()


@app.on_event("startup")
async def startup():
    await init_db()


@app.get("/")
async def root():
    return {
        "name": "Sports Betting Analyzer API",
        "version": "1.0.0",
        "endpoints": ["/picks", "/games", "/news", "/refresh"]
    }


@app.get("/picks")
async def get_picks(
    sport: Optional[str] = None,
    min_confidence: float = 60.0,
    limit: int = 10
):
    """Get today's top betting picks"""
    
    all_games = []
    sports_to_fetch = [sport] if sport else SPORTS
    
    # Fetch odds for all sports
    for s in sports_to_fetch:
        games = await odds_fetcher.get_odds(s)
        all_games.extend(games)
    
    # Get news sentiment
    news = news_fetcher.get_news()
    sentiment_map = {}
    for item in news:
        # Simple: use title words to map sentiment to teams
        for word in item["title"].split():
            if len(word) > 4:  # Skip short words
                sentiment_map[word] = item.get("sentiment", 0)
    
    # Generate picks
    picks = algorithm.generate_picks(
        all_games,
        news_sentiment=sentiment_map,
        min_confidence=min_confidence
    )
    
    return {
        "generated_at": datetime.utcnow().isoformat(),
        "total_games_analyzed": len(all_games),
        "picks_count": len(picks[:limit]),
        "picks": picks[:limit]
    }


@app.get("/games")
async def get_games(sport: Optional[str] = None):
    """Get all games with odds"""
    
    all_games = []
    sports_to_fetch = [sport] if sport else SPORTS
    
    for s in sports_to_fetch:
        games = await odds_fetcher.get_odds(s)
        all_games.extend(games)
    
    return {
        "count": len(all_games),
        "games": all_games
    }


@app.get("/games/{sport}")
async def get_games_by_sport(sport: str):
    """Get games for a specific sport"""
    
    if sport not in SPORTS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sport. Choose from: {SPORTS}"
        )
    
    games = await odds_fetcher.get_odds(sport)
    return {"sport": sport, "count": len(games), "games": games}


@app.get("/news")
async def get_news(limit: int = 20):
    """Get latest sports news with sentiment analysis"""
    
    news = news_fetcher.get_news(limit=limit)
    
    return {
        "count": len(news),
        "news": news
    }


@app.get("/sports")
async def get_sports():
    """Get list of supported sports"""
    
    sport_names = {
        "americanfootball_nfl": "NFL Football",
        "basketball_nba": "NBA Basketball",
        "baseball_mlb": "MLB Baseball",
        "icehockey_nhl": "NHL Hockey",
        "soccer_epl": "English Premier League",
    }
    
    return {
        "sports": [
            {"key": s, "name": sport_names.get(s, s)}
            for s in SPORTS
        ]
    }


@app.post("/refresh")
async def refresh_data():
    """Force refresh of all data"""
    
    all_games = []
    for sport in SPORTS:
        games = await odds_fetcher.get_odds(sport)
        all_games.extend(games)
    
    news = news_fetcher.get_news()
    
    return {
        "status": "refreshed",
        "games_fetched": len(all_games),
        "news_fetched": len(news),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/analyze/{game_id}")
async def analyze_game(game_id: str):
    """Get detailed analysis for a specific game"""
    
    # Find game across all sports
    for sport in SPORTS:
        games = await odds_fetcher.get_odds(sport)
        for game in games:
            if game.get("id") == game_id:
                analysis = algorithm.analyze_line_movement(game.get("bookmakers", []))
                picks = algorithm.generate_picks([game], min_confidence=0)
                
                return {
                    "game": game,
                    "analysis": analysis,
                    "picks": picks
                }
    
    raise HTTPException(status_code=404, detail="Game not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

