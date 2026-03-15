import httpx
import feedparser
from datetime import datetime
from typing import List, Dict, Any
from textblob import TextBlob
from config import ODDS_API_KEY, SPORTS, MARKETS


class OddsFetcher:
    """Fetches odds from The Odds API"""
    
    BASE_URL = "https://api.the-odds-api.com/v4"
    
    async def get_odds(self, sport: str) -> List[Dict[str, Any]]:
        """Fetch current odds for a sport"""
        if not ODDS_API_KEY:
            return self._get_mock_odds(sport)
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/sports/{sport}/odds",
                    params={
                        "apiKey": ODDS_API_KEY,
                        "regions": "us",
                        "markets": ",".join(MARKETS),
                        "oddsFormat": "american",
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Error fetching odds: {e}")
                return self._get_mock_odds(sport)
    
    def _get_mock_odds(self, sport: str) -> List[Dict[str, Any]]:
        """Return mock data for demo purposes"""
        from datetime import timedelta
        
        mock_games = {
            "americanfootball_nfl": [
                {"home": "Kansas City Chiefs", "away": "Las Vegas Raiders"},
                {"home": "Dallas Cowboys", "away": "New York Giants"},
                {"home": "San Francisco 49ers", "away": "Seattle Seahawks"},
            ],
            "basketball_nba": [
                {"home": "Los Angeles Lakers", "away": "Golden State Warriors"},
                {"home": "Boston Celtics", "away": "Miami Heat"},
                {"home": "Denver Nuggets", "away": "Phoenix Suns"},
            ],
            "baseball_mlb": [
                {"home": "New York Yankees", "away": "Boston Red Sox"},
                {"home": "Los Angeles Dodgers", "away": "San Francisco Giants"},
            ],
            "icehockey_nhl": [
                {"home": "Toronto Maple Leafs", "away": "Montreal Canadiens"},
                {"home": "Vegas Golden Knights", "away": "Colorado Avalanche"},
            ],
            "soccer_epl": [
                {"home": "Manchester United", "away": "Liverpool"},
                {"home": "Arsenal", "away": "Chelsea"},
            ],
        }
        
        games = mock_games.get(sport, [])
        result = []
        
        for i, game in enumerate(games):
            commence = datetime.utcnow() + timedelta(hours=i * 3 + 2)
            result.append({
                "id": f"{sport}_{i}_{datetime.utcnow().strftime('%Y%m%d')}",
                "sport_key": sport,
                "home_team": game["home"],
                "away_team": game["away"],
                "commence_time": commence.isoformat() + "Z",
                "bookmakers": [
                    {
                        "key": "draftkings",
                        "title": "DraftKings",
                        "markets": [
                            {
                                "key": "h2h",
                                "outcomes": [
                                    {"name": game["home"], "price": -150 + (i * 20)},
                                    {"name": game["away"], "price": 130 - (i * 10)},
                                ]
                            },
                            {
                                "key": "spreads",
                                "outcomes": [
                                    {"name": game["home"], "price": -110, "point": -3.5 - i},
                                    {"name": game["away"], "price": -110, "point": 3.5 + i},
                                ]
                            },
                            {
                                "key": "totals",
                                "outcomes": [
                                    {"name": "Over", "price": -110, "point": 45.5 + (i * 2)},
                                    {"name": "Under", "price": -110, "point": 45.5 + (i * 2)},
                                ]
                            }
                        ]
                    },
                    {
                        "key": "fanduel",
                        "title": "FanDuel",
                        "markets": [
                            {
                                "key": "h2h",
                                "outcomes": [
                                    {"name": game["home"], "price": -145 + (i * 15)},
                                    {"name": game["away"], "price": 125 - (i * 8)},
                                ]
                            }
                        ]
                    }
                ]
            })
        
        return result


class NewsFetcher:
    """Fetches sports news from RSS feeds"""
    
    RSS_FEEDS = {
        "espn_nfl": "https://www.espn.com/espn/rss/nfl/news",
        "espn_nba": "https://www.espn.com/espn/rss/nba/news",
        "espn_mlb": "https://www.espn.com/espn/rss/mlb/news",
    }
    
    def get_news(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch recent sports news"""
        news_items = []
        
        for source, url in self.RSS_FEEDS.items():
            try:
                feed = feedparser.parse(url)
                sport = source.split("_")[1].upper()
                
                for entry in feed.entries[:limit // len(self.RSS_FEEDS)]:
                    summary = entry.get("summary", entry.get("title", ""))
                    sentiment = TextBlob(summary).sentiment.polarity
                    
                    news_items.append({
                        "title": entry.get("title", ""),
                        "summary": summary[:500],
                        "source": source,
                        "sport": sport,
                        "sentiment": sentiment,
                        "published_at": entry.get("published", datetime.utcnow().isoformat()),
                    })
            except Exception as e:
                print(f"Error fetching news from {source}: {e}")
        
        return news_items

