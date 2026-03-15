import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime


class BettingAlgorithm:
    """Core algorithm for analyzing betting value"""
    
    def __init__(self):
        # Weight factors for confidence scoring
        self.weights = {
            "odds_value": 0.35,
            "line_consensus": 0.25,
            "market_efficiency": 0.20,
            "recency": 0.10,
            "sentiment": 0.10,
        }
    
    def american_to_implied_prob(self, odds: int) -> float:
        """Convert American odds to implied probability"""
        if odds > 0:
            return 100 / (odds + 100)
        else:
            return abs(odds) / (abs(odds) + 100)
    
    def implied_prob_to_american(self, prob: float) -> int:
        """Convert implied probability to American odds"""
        if prob >= 0.5:
            return int(-100 * prob / (1 - prob))
        else:
            return int(100 * (1 - prob) / prob)
    
    def calculate_ev(self, odds: int, estimated_win_prob: float) -> float:
        """Calculate expected value of a bet"""
        implied_prob = self.american_to_implied_prob(odds)
        
        if odds > 0:
            profit = odds / 100
        else:
            profit = 100 / abs(odds)
        
        ev = (estimated_win_prob * profit) - ((1 - estimated_win_prob) * 1)
        return round(ev * 100, 2)  # Return as percentage
    
    def analyze_line_movement(self, bookmakers: List[Dict]) -> Dict[str, Any]:
        """Analyze odds across bookmakers for value"""
        if not bookmakers:
            return {"consensus": None, "spread": 0, "best_odds": {}}
        
        all_odds = {}
        
        for book in bookmakers:
            for market in book.get("markets", []):
                market_key = market["key"]
                if market_key not in all_odds:
                    all_odds[market_key] = {}
                
                for outcome in market.get("outcomes", []):
                    name = outcome["name"]
                    price = outcome["price"]
                    point = outcome.get("point")
                    
                    key = f"{name}_{point}" if point else name
                    if key not in all_odds[market_key]:
                        all_odds[market_key][key] = []
                    all_odds[market_key][key].append(price)
        
        # Find best odds and consensus
        best_odds = {}
        consensus = {}
        
        for market, outcomes in all_odds.items():
            best_odds[market] = {}
            for outcome, prices in outcomes.items():
                # Best odds = highest for positive, lowest magnitude for negative
                best = max(prices) if max(prices) > 0 else max(prices)
                best_odds[market][outcome] = best
                consensus[f"{market}_{outcome}"] = np.mean(prices)
        
        return {
            "best_odds": best_odds,
            "consensus": consensus,
            "spread": max([np.std(p) for p in all_odds.get("h2h", {}).values()] or [0])
        }
    
    def estimate_win_probability(
        self,
        odds: int,
        consensus_odds: float,
        line_spread: float,
        sentiment: float = 0
    ) -> float:
        """
        Estimate true win probability using multiple factors.
        This is a simplified model - production would use ML.
        """
        # Start with implied probability from consensus
        base_prob = self.american_to_implied_prob(int(consensus_odds))
        
        # Remove vig (assume ~4.5% total vig, split evenly)
        no_vig_prob = base_prob / 1.045
        
        # Adjust for line movement (larger spread = less certain)
        movement_factor = 1 - (min(line_spread, 20) / 100)
        
        # Adjust for sentiment (-1 to 1 scale)
        sentiment_adj = sentiment * 0.02  # Max 2% adjustment
        
        estimated_prob = no_vig_prob * movement_factor + sentiment_adj
        return max(0.1, min(0.9, estimated_prob))  # Clamp between 10-90%
    
    def generate_picks(
        self,
        games: List[Dict[str, Any]],
        news_sentiment: Dict[str, float] = None,
        min_ev: float = 2.0,
        min_confidence: float = 60.0
    ) -> List[Dict[str, Any]]:
        """Generate betting picks from games data"""
        
        if news_sentiment is None:
            news_sentiment = {}
        
        picks = []
        
        for game in games:
            game_id = game.get("id", "")
            sport = game.get("sport_key", "")
            home = game.get("home_team", "")
            away = game.get("away_team", "")
            bookmakers = game.get("bookmakers", [])
            
            if not bookmakers:
                continue
            
            analysis = self.analyze_line_movement(bookmakers)
            best_odds = analysis.get("best_odds", {})
            line_spread = analysis.get("spread", 0)
            
            # Analyze each market
            for market_type, outcomes in best_odds.items():
                for outcome_key, odds in outcomes.items():
                    # Get team name from outcome key
                    team = outcome_key.split("_")[0]
                    
                    # Get sentiment for team
                    sentiment = news_sentiment.get(team, 0)
                    
                    # Get consensus odds
                    consensus_key = f"{market_type}_{outcome_key}"
                    consensus = analysis["consensus"].get(consensus_key, odds)
                    
                    # Estimate win probability
                    win_prob = self.estimate_win_probability(
                        odds, consensus, line_spread, sentiment
                    )
                    
                    # Calculate EV
                    ev = self.calculate_ev(odds, win_prob)
                    
                    # Calculate confidence score
                    confidence = self._calculate_confidence(
                        ev, line_spread, abs(sentiment), win_prob
                    )
                    
                    # Filter by thresholds
                    if ev >= min_ev and confidence >= min_confidence:
                        pick_type = {
                            "h2h": "moneyline",
                            "spreads": "spread", 
                            "totals": "total"
                        }.get(market_type, market_type)
                        
                        reasoning = self._generate_reasoning(
                            team, pick_type, odds, ev, win_prob, line_spread
                        )
                        
                        picks.append({
                            "game_id": game_id,
                            "sport": sport,
                            "home_team": home,
                            "away_team": away,
                            "pick_type": pick_type,
                            "pick": outcome_key,
                            "odds": odds,
                            "confidence": round(confidence, 1),
                            "ev_score": ev,
                            "win_probability": round(win_prob * 100, 1),
                            "reasoning": reasoning,
                            "commence_time": game.get("commence_time"),
                        })
        
        # Sort by confidence and return top picks
        picks.sort(key=lambda x: (x["confidence"], x["ev_score"]), reverse=True)
        return picks[:10]  # Return top 10 picks
    
    def _calculate_confidence(
        self,
        ev: float,
        line_spread: float,
        sentiment_strength: float,
        win_prob: float
    ) -> float:
        """Calculate confidence score (0-100)"""
        
        # EV component (0-35 points)
        ev_score = min(35, max(0, ev * 3.5))
        
        # Line consensus component (0-25 points) - lower spread = higher confidence
        consensus_score = max(0, 25 - line_spread)
        
        # Market efficiency (0-20 points) - closer to 50% = more efficient market
        efficiency = 20 - abs(win_prob - 0.5) * 40
        
        # Sentiment confirmation (0-10 points)
        sentiment_score = sentiment_strength * 10
        
        # Win probability bonus (0-10 points)
        prob_score = win_prob * 10 if win_prob > 0.5 else (1 - win_prob) * 5
        
        total = ev_score + consensus_score + efficiency + sentiment_score + prob_score
        return min(100, max(0, total))
    
    def _generate_reasoning(
        self,
        team: str,
        pick_type: str,
        odds: int,
        ev: float,
        win_prob: float,
        line_spread: float
    ) -> str:
        """Generate human-readable reasoning for pick"""
        
        reasons = []
        
        if ev > 5:
            reasons.append(f"Strong +{ev:.1f}% expected value")
        elif ev > 2:
            reasons.append(f"Positive +{ev:.1f}% expected value")
        
        if line_spread < 5:
            reasons.append("tight line consensus across books")
        elif line_spread > 15:
            reasons.append("significant line movement detected")
        
        if win_prob > 0.6:
            reasons.append(f"estimated {win_prob*100:.0f}% win probability")
        
        odds_str = f"+{odds}" if odds > 0 else str(odds)
        
        base = f"{team} {pick_type} at {odds_str}"
        if reasons:
            return f"{base} — {', '.join(reasons)}."
        return base

