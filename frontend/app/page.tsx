'use client'

import { useState, useEffect } from 'react'
import { RefreshCw, TrendingUp, Target, Zap, Trophy, Clock } from 'lucide-react'

interface Pick {
  game_id: string
  sport: string
  home_team: string
  away_team: string
  pick_type: string
  pick: string
  odds: number
  confidence: number
  ev_score: number
  win_probability: number
  reasoning: string
  commence_time: string
}

interface PicksResponse {
  generated_at: string
  total_games_analyzed: number
  picks_count: number
  picks: Pick[]
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const sportEmojis: Record<string, string> = {
  americanfootball_nfl: '🏈',
  basketball_nba: '🏀',
  baseball_mlb: '⚾',
  icehockey_nhl: '🏒',
  soccer_epl: '⚽',
}

const sportNames: Record<string, string> = {
  americanfootball_nfl: 'NFL',
  basketball_nba: 'NBA',
  baseball_mlb: 'MLB',
  icehockey_nhl: 'NHL',
  soccer_epl: 'EPL',
}

export default function Home() {
  const [picks, setPicks] = useState<Pick[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState<string>('all')
  const [stats, setStats] = useState({
    gamesAnalyzed: 0,
    avgConfidence: 0,
    avgEV: 0,
    topPick: 0,
  })

  const fetchPicks = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const url = filter === 'all' 
        ? `${API_URL}/picks`
        : `${API_URL}/picks?sport=${filter}`
      
      const res = await fetch(url)
      
      if (!res.ok) throw new Error('Failed to fetch picks')
      
      const data: PicksResponse = await res.json()
      setPicks(data.picks)
      
      // Calculate stats
      const avgConf = data.picks.length > 0
        ? data.picks.reduce((sum, p) => sum + p.confidence, 0) / data.picks.length
        : 0
      const avgEV = data.picks.length > 0
        ? data.picks.reduce((sum, p) => sum + p.ev_score, 0) / data.picks.length
        : 0
      
      setStats({
        gamesAnalyzed: data.total_games_analyzed,
        avgConfidence: Math.round(avgConf),
        avgEV: Math.round(avgEV * 10) / 10,
        topPick: data.picks[0]?.confidence || 0,
      })
    } catch (err) {
      setError('Unable to connect to API. Make sure the backend is running.')
      // Load demo data
      loadDemoData()
    } finally {
      setLoading(false)
    }
  }

  const loadDemoData = () => {
    const demoPicks: Pick[] = [
      {
        game_id: 'demo_1',
        sport: 'americanfootball_nfl',
        home_team: 'Kansas City Chiefs',
        away_team: 'Las Vegas Raiders',
        pick_type: 'spread',
        pick: 'Kansas City Chiefs_-6.5',
        odds: -110,
        confidence: 78.5,
        ev_score: 4.2,
        win_probability: 68,
        reasoning: 'Kansas City Chiefs spread at -110 — Strong +4.2% expected value, tight line consensus across books.',
        commence_time: new Date(Date.now() + 3600000 * 5).toISOString(),
      },
      {
        game_id: 'demo_2',
        sport: 'basketball_nba',
        home_team: 'Los Angeles Lakers',
        away_team: 'Golden State Warriors',
        pick_type: 'moneyline',
        pick: 'Golden State Warriors',
        odds: 145,
        confidence: 72.3,
        ev_score: 5.8,
        win_probability: 52,
        reasoning: 'Golden State Warriors moneyline at +145 — Strong +5.8% expected value, estimated 52% win probability.',
        commence_time: new Date(Date.now() + 3600000 * 8).toISOString(),
      },
      {
        game_id: 'demo_3',
        sport: 'icehockey_nhl',
        home_team: 'Toronto Maple Leafs',
        away_team: 'Montreal Canadiens',
        pick_type: 'total',
        pick: 'Over_6.5',
        odds: -105,
        confidence: 69.8,
        ev_score: 3.1,
        win_probability: 58,
        reasoning: 'Over 6.5 at -105 — Positive +3.1% expected value, both teams averaging high scoring games recently.',
        commence_time: new Date(Date.now() + 3600000 * 4).toISOString(),
      },
      {
        game_id: 'demo_4',
        sport: 'americanfootball_nfl',
        home_team: 'Dallas Cowboys',
        away_team: 'New York Giants',
        pick_type: 'moneyline',
        pick: 'Dallas Cowboys',
        odds: -180,
        confidence: 67.2,
        ev_score: 2.4,
        win_probability: 72,
        reasoning: 'Dallas Cowboys moneyline at -180 — Positive +2.4% expected value, estimated 72% win probability.',
        commence_time: new Date(Date.now() + 3600000 * 26).toISOString(),
      },
      {
        game_id: 'demo_5',
        sport: 'basketball_nba',
        home_team: 'Boston Celtics',
        away_team: 'Miami Heat',
        pick_type: 'spread',
        pick: 'Boston Celtics_-4.5',
        odds: -108,
        confidence: 65.1,
        ev_score: 2.9,
        win_probability: 61,
        reasoning: 'Boston Celtics spread at -108 — Positive +2.9% expected value, tight line consensus across books.',
        commence_time: new Date(Date.now() + 3600000 * 7).toISOString(),
      },
    ]
    
    setPicks(demoPicks)
    setStats({
      gamesAnalyzed: 14,
      avgConfidence: 71,
      avgEV: 3.7,
      topPick: 78.5,
    })
  }

  useEffect(() => {
    fetchPicks()
  }, [filter])

  const formatOdds = (odds: number) => {
    return odds > 0 ? `+${odds}` : odds.toString()
  }

  const formatTime = (isoString: string) => {
    const date = new Date(isoString)
    return date.toLocaleString('en-US', {
      weekday: 'short',
      hour: 'numeric',
      minute: '2-digit',
    })
  }

  const formatPick = (pick: string) => {
    // Handle spread/total picks like "Team_-6.5" or "Over_45.5"
    const parts = pick.split('_')
    if (parts.length === 2) {
      const [name, value] = parts
      if (name === 'Over' || name === 'Under') {
        return `${name} ${value}`
      }
      return `${name} ${parseFloat(value) > 0 ? '+' : ''}${value}`
    }
    return pick
  }

  return (
    <div className="container">
      <header>
        <div className="logo">
          <div className="logo-icon">🎯</div>
          <div>
            <h1>BetBrain</h1>
            <span>AI-Powered Betting Analysis</span>
          </div>
        </div>
        <button 
          className={`refresh-btn ${loading ? 'loading' : ''}`}
          onClick={fetchPicks}
          disabled={loading}
        >
          {loading ? <span className="loading-spinner" /> : <RefreshCw size={18} />}
          {loading ? 'Analyzing...' : 'Refresh Picks'}
        </button>
      </header>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Games Analyzed</div>
          <div className="stat-value">{stats.gamesAnalyzed}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Avg Confidence</div>
          <div className="stat-value green">{stats.avgConfidence}%</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Avg Expected Value</div>
          <div className="stat-value gold">+{stats.avgEV}%</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Top Pick Confidence</div>
          <div className="stat-value blue">{stats.topPick}%</div>
        </div>
      </div>

      <div className="section-header">
        <h2 className="section-title">
          <Trophy size={20} />
          Today's Top Picks
        </h2>
        <div className="filters">
          <button 
            className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            All Sports
          </button>
          <button 
            className={`filter-btn ${filter === 'americanfootball_nfl' ? 'active' : ''}`}
            onClick={() => setFilter('americanfootball_nfl')}
          >
            🏈 NFL
          </button>
          <button 
            className={`filter-btn ${filter === 'basketball_nba' ? 'active' : ''}`}
            onClick={() => setFilter('basketball_nba')}
          >
            🏀 NBA
          </button>
          <button 
            className={`filter-btn ${filter === 'icehockey_nhl' ? 'active' : ''}`}
            onClick={() => setFilter('icehockey_nhl')}
          >
            🏒 NHL
          </button>
        </div>
      </div>

      {error && (
        <div style={{ 
          padding: '1rem', 
          background: 'rgba(239, 68, 68, 0.1)', 
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: '8px',
          marginBottom: '1rem',
          color: '#ef4444',
          fontSize: '0.9rem'
        }}>
          ⚠️ {error} — Showing demo data.
        </div>
      )}

      <div className="picks-list">
        {picks.length === 0 && !loading ? (
          <div className="empty-state">
            <h3>No picks available</h3>
            <p>Check back later for new betting opportunities</p>
          </div>
        ) : (
          picks.map((pick, index) => (
            <div key={pick.game_id + pick.pick} className="pick-card">
              <div className="pick-rank">{index + 1}</div>
              
              <div className="pick-info">
                <div style={{ marginBottom: '0.5rem' }}>
                  <span className="sport-badge">
                    {sportEmojis[pick.sport]} {sportNames[pick.sport]}
                  </span>
                  <span className="pick-type">{pick.pick_type}</span>
                  <span className="time-badge">
                    <Clock size={12} style={{ marginRight: '4px', verticalAlign: 'middle' }} />
                    {formatTime(pick.commence_time)}
                  </span>
                </div>
                <h3>{formatPick(pick.pick)}</h3>
                <div className="matchup">{pick.away_team} @ {pick.home_team}</div>
                <div className="reasoning">{pick.reasoning}</div>
              </div>

              <div className="pick-metrics">
                <div className="metric">
                  <span className="metric-label">Odds</span>
                  <span className="metric-value odds">{formatOdds(pick.odds)}</span>
                </div>
                <div className="metric">
                  <span className="metric-label">EV</span>
                  <span className="metric-value ev">+{pick.ev_score}%</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Win %</span>
                  <span className="metric-value">{pick.win_probability}%</span>
                </div>
              </div>

              <div className="confidence-meter">
                <div 
                  className="confidence-ring"
                  style={{ '--confidence': pick.confidence } as React.CSSProperties}
                >
                  <span className="confidence-value">{Math.round(pick.confidence)}</span>
                </div>
                <span className="confidence-label">Confidence</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

