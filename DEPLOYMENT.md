# Deploying BetBrain

This guide gets the app running in production: backend API first, then frontend pointing at it.

## What you need

- **Backend:** Python 3.9+ host (Render, Railway, Fly.io, etc.)
- **Frontend:** Node.js host (Vercel, Netlify, or same platform as backend)
- **API key:** [The Odds API](https://the-odds-api.com/) (free tier is enough)

---

## 1. Deploy the backend (Python/FastAPI)

Deploy the `backend/` folder. The app uses `PORT` from the environment, so it works on Render, Railway, Fly.io, and similar hosts.

### Option A: Render

1. Create a **Web Service**, connect your repo, set **Root Directory** to `backend`.
2. **Build:** `pip install -r requirements.txt`
3. **Start:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. **Environment variables:**
   - `ODDS_API_KEY` = your key from the-odds-api.com
   - `DATABASE_URL` = leave default or use `sqlite+aiosqlite:///./betting.db` (ephemeral on free tier)
   - `PORT` is set automatically by Render.
5. Deploy. Note the service URL (e.g. `https://your-app.onrender.com`).

### Option B: Railway

1. New project → Deploy from repo, set **Root Directory** to `backend`.
2. Railway detects Python. Ensure start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. In **Variables**, add `ODDS_API_KEY`.
4. Deploy and copy the public URL.

### Option C: Fly.io

1. In `backend/`: `fly launch` (or create `fly.toml` with `backend/` as app dir).
2. Set secret: `fly secrets set ODDS_API_KEY=your_key`
3. Ensure the app listens on `PORT` (default 8080 on Fly). In `main.py` the app already uses `config.PORT`, and Fly sets `PORT`; if you use 8000 by default, set `PORT=8080` in `fly.toml` env or use Fly’s `PORT` (often 8080).
4. Deploy: `fly deploy`.

After deployment, open `https://your-backend-url/` — you should see the API JSON (name, version, endpoints).

---

## 2. Deploy the frontend (Next.js)

Deploy the `frontend/` folder and point it at your backend URL.

### Option A: Vercel (recommended for Next.js)

1. Import your repo in [Vercel](https://vercel.com). Set **Root Directory** to `frontend`.
2. **Environment variable:** add `NEXT_PUBLIC_API_URL` = your backend URL (e.g. `https://your-app.onrender.com`). No trailing slash.
3. Deploy. Vercel will build and host the app.

### Option B: Netlify

1. New site from repo, **Base directory** = `frontend`.
2. **Build command:** `npm run build`
3. **Publish directory:** `.next` (or use Netlify’s Next.js plugin; they may set this automatically).
4. **Environment variable:** `NEXT_PUBLIC_API_URL` = your backend URL.
5. Deploy.

### Option C: Same platform as backend (e.g. Render)

1. Create a second **Web Service** (or Static Site if the platform supports Next.js), root = `frontend`.
2. **Build:** `npm install && npm run build`
3. **Start:** `npm start` (or the platform’s default for Next.js).
4. Set `NEXT_PUBLIC_API_URL` to your backend URL.

---

## 3. Checklist

| Where        | Variable               | Example / notes                          |
|-------------|------------------------|------------------------------------------|
| Backend     | `ODDS_API_KEY`         | From the-odds-api.com                    |
| Backend     | `DATABASE_URL`         | Optional; default SQLite path is fine    |
| Backend     | `PORT`                 | Usually set by host (Render, Railway…)   |
| Frontend    | `NEXT_PUBLIC_API_URL`  | `https://your-backend.onrender.com`      |

- Backend CORS is set to allow all origins, so the frontend can call it from any domain.
- After deployment, open the frontend URL; the dashboard will call the backend for picks. If the backend is unreachable, the app falls back to demo data.

---

## 4. Run locally (same as before)

**Backend**

```bash
cd backend
python -m venv venv && source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env   # add your ODDS_API_KEY
python main.py
```

**Frontend**

```bash
cd frontend
npm install
cp .env.example .env.local   # optional; defaults to http://localhost:8000
npm run dev
```

Backend: http://localhost:8000  
Frontend: http://localhost:3000  
