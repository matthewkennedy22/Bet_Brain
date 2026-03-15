# BetBrain - AI Sports Betting Analyzer

**By [@matthewkennedy22](https://github.com/matthewkennedy22)**

An AI-powered app that aggregates sports statistics, news, and betting odds to identify high-value betting opportunities.

![BetBrain Dashboard](https://via.placeholder.com/800x400/0a0e17/10b981?text=BetBrain+Dashboard)

## Features

-  **Smart Picks** - Algorithm-generated betting recommendations
-  **Expected Value Analysis** - Calculates +EV opportunities
-  **News Sentiment** - Incorporates sports news into analysis
-  **Real-time Odds** - Pulls live odds from multiple sportsbooks
- **Confidence Scoring** - Ranks picks by confidence level

## Supported Sports

-  NFL Football
-  NBA Basketball
-  MLB Baseball
-  NHL Hockey
-  English Premier League

## Quick Start

### Backend Setup

```bash
cd betting-analyzer/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Add your API key for live odds
# Copy .env.example to .env and add your key from https://the-odds-api.com/
cp .env.example .env

# Run the API server
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

```bash
cd betting-analyzer/frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The dashboard will be available at `http://localhost:3000`

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /picks` | Get today's top betting picks |
| `GET /games` | Get all games with odds |
| `GET /games/{sport}` | Get games for specific sport |
| `GET /news` | Get sports news with sentiment |
| `GET /sports` | List supported sports |
| `POST /refresh` | Force refresh all data |
| `GET /analyze/{game_id}` | Detailed analysis for a game |

### Query Parameters

- `sport` - Filter by sport key (e.g., `basketball_nba`)
- `min_confidence` - Minimum confidence threshold (default: 60)
- `limit` - Max picks to return (default: 10)

## Algorithm Overview

The betting algorithm analyzes:

1. **Line Movement** - Compares odds across multiple sportsbooks
2. **Expected Value (EV)** - Calculates edge vs. implied probability
3. **Market Consensus** - Measures agreement between books
4. **News Sentiment** - NLP analysis of sports news
5. **Win Probability** - Estimates true win % after removing vig

### Confidence Score Components

- Odds Value (35%) - Higher EV = higher confidence
- Line Consensus (25%) - Tighter lines = more confidence
- Market Efficiency (20%) - Accounts for market uncertainty
- Sentiment (10%) - News sentiment confirmation
- Win Probability (10%) - Bonus for favorable probability

## Configuration

### Environment Variables

```
ODDS_API_KEY=your_api_key_here  # Get free key at the-odds-api.com
DATABASE_URL=sqlite+aiosqlite:///./betting.db
```

### Customization

Edit `backend/config.py` to:
- Add/remove supported sports
- Change betting markets analyzed
- Adjust algorithm parameters

## Tech Stack

**Backend:**
- Python 3.10+
- FastAPI
- SQLAlchemy (async)
- Pandas/NumPy
- TextBlob (sentiment)

**Frontend:**
- Next.js 14
- React 18
- TypeScript
- Lucide Icons

## Disclaimer

⚠️ **This app is for educational and entertainment purposes only.**

- Past performance does not guarantee future results
- Always gamble responsibly
- Check local laws regarding sports betting
- Never bet more than you can afford to lose

## Pushing to a repo

The repo is set up so only source and config are tracked; dependencies and build artifacts are ignored (see `.gitignore`). This keeps the repo small and under typical size limits.

- **Excluded:** `node_modules/`, `venv/`, `.next/`, `.env`, `*.db`, and other generated/cache files.
- **Included:** All app code, `package.json`, `requirements.txt`, and `backend/.env.example` (copy to `.env` and add your API key).

After cloning, run backend and frontend setup from the Quick Start section above.

## License

MIT
