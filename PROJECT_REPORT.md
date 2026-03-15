# BetBrain: AI-Powered Sports Betting Analyzer
## Technical Project Report

---

## Executive Summary

BetBrain is a full-stack web application that aggregates real-time sports betting odds from multiple sportsbooks and applies a proprietary algorithm to identify high-value betting opportunities. The system analyzes odds across major sports leagues, incorporates news sentiment analysis, and calculates expected value (EV) and confidence scores to surface the most promising bets each day.

**Key Technologies:** Python, FastAPI, Next.js, React, TypeScript, SQLite, REST APIs

**Development Approach:** AI-assisted development using Cursor IDE with iterative refinement

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Algorithm Deep Dive](#algorithm-deep-dive)
4. [Data Sources](#data-sources)
5. [Technical Implementation](#technical-implementation)
6. [Future Enhancements](#future-enhancements)

---

## Project Overview

### Problem Statement

Sports bettors face several challenges:
- Manually comparing odds across multiple sportsbooks is time-consuming
- Identifying true value bets requires complex probability calculations
- News and injury information isn't systematically factored into betting decisions
- No centralized tool combines odds aggregation with analytical recommendations

### Solution

BetBrain addresses these challenges by:
1. **Aggregating odds** from multiple sportsbooks in real-time
2. **Calculating expected value** for every betting opportunity
3. **Analyzing news sentiment** to factor in market-moving information
4. **Generating confidence scores** to rank betting opportunities
5. **Presenting picks** through an intuitive, modern dashboard

### Supported Sports

| Sport | League | API Key |
|-------|--------|---------|
| Football | NFL | `americanfootball_nfl` |
| Basketball | NBA | `basketball_nba` |
| Baseball | MLB | `baseball_mlb` |
| Hockey | NHL | `icehockey_nhl` |
| Soccer | English Premier League | `soccer_epl` |

---

## System Architecture

### High-Level Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   Odds API      │────▶│   FastAPI       │────▶│   Next.js       │
│   (External)    │     │   Backend       │     │   Frontend      │
│                 │     │                 │     │                 │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
┌─────────────────┐              │
│                 │              │
│   News RSS      │──────────────┤
│   Feeds         │              │
│                 │              │
└─────────────────┘              │
                                 ▼
                        ┌─────────────────┐
                        │                 │
                        │   SQLite        │
                        │   Database      │
                        │                 │
                        └─────────────────┘
```

### Backend Components

| File | Purpose |
|------|---------|
| `main.py` | FastAPI application with REST endpoints |
| `algorithm.py` | Core betting analysis algorithm |
| `data_fetcher.py` | Odds API and news RSS integration |
| `models.py` | SQLAlchemy database models |
| `database.py` | Async database configuration |
| `config.py` | Environment and settings management |

### Frontend Components

| File | Purpose |
|------|---------|
| `app/page.tsx` | Main dashboard with picks display |
| `app/layout.tsx` | Application layout and metadata |
| `app/globals.css` | Dark theme styling with CSS variables |

---

## Algorithm Deep Dive

### Overview

The BetBrain algorithm generates a **confidence score (0-100)** for each potential bet by analyzing five key factors. Only bets meeting minimum thresholds for both Expected Value (≥2%) and Confidence (≥60%) are surfaced to users.

### Confidence Score Components

The confidence score is calculated as the sum of five weighted components:

#### 1. Expected Value Score (0-35 points) — 35% Weight

```python
ev_score = min(35, max(0, ev * 3.5))
```

**What it measures:** The mathematical edge of the bet

**How it works:**
- Expected Value (EV) represents the average profit/loss per bet if placed infinitely
- Formula: `EV = (Win Probability × Profit) - (Loss Probability × Stake)`
- The EV percentage is multiplied by 3.5 to scale to 35 points max

**Example:**
- +10% EV → 35 points (maximum)
- +5% EV → 17.5 points
- +2% EV → 7 points

#### 2. Line Consensus Score (0-25 points) — 25% Weight

```python
consensus_score = max(0, 25 - line_spread)
```

**What it measures:** Agreement between sportsbooks on the odds

**How it works:**
- Calculates the standard deviation of odds across all bookmakers
- Lower spread = books agree = more accurate line = higher confidence
- If spread exceeds 25, score becomes 0

**Example:**
- All books at -110 (spread = 0) → 25 points
- Books range -105 to -115 (spread = 5) → 20 points
- Books range -100 to -130 (spread = 15) → 10 points

#### 3. Market Efficiency Score (0-20 points) — 20% Weight

```python
efficiency = 20 - abs(win_prob - 0.5) * 40
```

**What it measures:** How liquid/efficient the betting market is

**How it works:**
- Markets closer to 50/50 are typically more efficient (more betting action)
- More efficient markets = more reliable probability estimates
- Heavily favored or underdog lines may have less reliable data

**Example:**
- 50% win probability → 20 points (maximum)
- 60% win probability → 16 points
- 75% win probability → 10 points

#### 4. Sentiment Score (0-10 points) — 10% Weight

```python
sentiment_score = sentiment_strength * 10
```

**What it measures:** News sentiment confirmation

**How it works:**
- Analyzes sports news headlines using Natural Language Processing (TextBlob)
- Sentiment ranges from -1 (negative) to +1 (positive)
- Strong sentiment in either direction adds confidence that market may not have fully adjusted

**Example:**
- Strong positive news (0.8 sentiment) → 8 points
- Neutral news (0.2 sentiment) → 2 points
- No relevant news (0 sentiment) → 0 points

#### 5. Win Probability Bonus (0-10 points) — 10% Weight

```python
prob_score = win_prob * 10 if win_prob > 0.5 else (1 - win_prob) * 5
```

**What it measures:** Baseline likelihood of winning

**How it works:**
- Favorites (>50% win probability) receive up to 10 bonus points
- Underdogs receive up to 5 bonus points
- Provides slight bias toward safer bets

**Example:**
- 70% favorite → 7 points
- 55% slight favorite → 5.5 points
- 40% underdog → 3 points

### Final Confidence Calculation

```python
total = ev_score + consensus_score + efficiency + sentiment_score + prob_score
confidence = min(100, max(0, total))  # Clamped between 0-100
```

### Complete Example

**Scenario:** Kansas City Chiefs -3.5 spread at -108

| Factor | Value | Calculation | Points |
|--------|-------|-------------|--------|
| Expected Value | +6.2% | 6.2 × 3.5 | 21.7 |
| Line Spread | 2.5 | 25 - 2.5 | 22.5 |
| Win Probability | 58% | 20 - \|0.58-0.5\| × 40 | 16.8 |
| Sentiment | 0.35 | 0.35 × 10 | 3.5 |
| Win Prob Bonus | 58% | 0.58 × 10 | 5.8 |
| **TOTAL** | | | **70.3** |

**Result:** 70.3% confidence score — This pick would be surfaced to users.

---

## Data Sources

### The Odds API

**Provider:** [the-odds-api.com](https://the-odds-api.com)

**Data Retrieved:**
- Real-time odds from 10+ US sportsbooks
- Moneyline, spread, and totals markets
- Game start times and team information

**Sportsbooks Included:**
- DraftKings
- FanDuel
- BetMGM
- Caesars
- PointsBet
- And others...

### News RSS Feeds

**Sources:**
- ESPN NFL News
- ESPN NBA News
- ESPN MLB News

**Processing:**
- Headlines parsed via feedparser library
- Sentiment analysis via TextBlob NLP
- Team mentions extracted and mapped to games

---

## Technical Implementation

### Backend Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.9+ | Core language |
| FastAPI | 0.115.0 | REST API framework |
| SQLAlchemy | 2.0.35 | Async ORM |
| aiosqlite | 0.20.0 | Async SQLite driver |
| Pandas | 2.0.3 | Data manipulation |
| NumPy | 1.26.4 | Numerical calculations |
| TextBlob | 0.18.0 | Sentiment analysis |
| httpx | 0.27.0 | Async HTTP client |

### Frontend Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 14.0.3 | React framework |
| React | 18.2.0 | UI library |
| TypeScript | 5.3.2 | Type safety |
| Lucide React | 0.294.0 | Icons |

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/picks` | Get today's top betting picks |
| GET | `/games` | Get all games with odds |
| GET | `/games/{sport}` | Get games for specific sport |
| GET | `/news` | Get sports news with sentiment |
| GET | `/sports` | List supported sports |
| POST | `/refresh` | Force refresh all data |
| GET | `/analyze/{game_id}` | Detailed analysis for a game |

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sport` | string | all | Filter by sport key |
| `min_confidence` | float | 60.0 | Minimum confidence threshold |
| `limit` | int | 10 | Maximum picks to return |

---

## Database Schema

### Games Table

```sql
CREATE TABLE games (
    id VARCHAR PRIMARY KEY,
    sport VARCHAR,
    home_team VARCHAR,
    away_team VARCHAR,
    commence_time DATETIME,
    odds_data JSON,
    created_at DATETIME
);
```

### Bet Picks Table

```sql
CREATE TABLE bet_picks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id VARCHAR,
    sport VARCHAR,
    pick_type VARCHAR,
    pick VARCHAR,
    odds INTEGER,
    confidence FLOAT,
    ev_score FLOAT,
    reasoning VARCHAR,
    created_at DATETIME,
    result VARCHAR
);
```

### News Table

```sql
CREATE TABLE news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR,
    summary VARCHAR,
    source VARCHAR,
    sport VARCHAR,
    sentiment FLOAT,
    teams_mentioned JSON,
    published_at DATETIME,
    created_at DATETIME
);
```

---

## Future Enhancements

### Short-term Improvements

1. **Historical Tracking** — Log all picks and track win/loss record over time
2. **User Accounts** — Allow users to save preferences and track their bets
3. **Push Notifications** — Alert users when high-confidence picks emerge
4. **More Sports** — Add college football, college basketball, UFC, tennis

### Long-term Vision

1. **Machine Learning Model** — Replace heuristic algorithm with trained ML model using historical betting data
2. **Injury Integration** — Pull real-time injury reports and factor into probability estimates
3. **Sharp Money Indicators** — Track line movements to identify professional bettor activity
4. **Bankroll Management** — Suggest bet sizing based on Kelly Criterion
5. **Mobile App** — Native iOS/Android applications

---

## Development Process

### AI-Assisted Development

This project was built using **Cursor IDE** with AI assistance, demonstrating modern AI-augmented software development practices:

1. **Architecture Planning** — AI helped design the system architecture and component structure
2. **Code Generation** — Core algorithm and API endpoints were generated with AI assistance
3. **Debugging** — AI helped diagnose and resolve dependency and runtime issues
4. **Documentation** — This report was generated with AI assistance

### Development Timeline

| Phase | Duration | Activities |
|-------|----------|------------|
| Planning | 1 hour | Requirements, architecture design |
| Backend | 2 hours | API, algorithm, data fetching |
| Frontend | 2 hours | Dashboard UI, styling |
| Integration | 1 hour | Testing, debugging, deployment |

---

## Conclusion

BetBrain demonstrates a practical application of data aggregation, algorithmic analysis, and modern web development. The confidence scoring algorithm provides a transparent, explainable method for ranking betting opportunities, while the clean architecture allows for future enhancements and scaling.

The project showcases proficiency in:
- Full-stack web development (Python + React)
- REST API design
- Algorithm development
- Data analysis and aggregation
- AI-assisted development workflows

---

## Appendix: Running the Application

### Backend Setup

```bash
cd betting-analyzer/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Create .env file with ODDS_API_KEY
python main.py
```

### Frontend Setup

```bash
cd betting-analyzer/frontend
npm install
npm run dev
```

### Access Points

- **Frontend Dashboard:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

---

*Report generated for BetBrain v1.0.0*
*Development assisted by Cursor AI*

