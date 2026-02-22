from fastapi import FastAPI
import httpx
import os
import time
import random

app = FastAPI()

API_KEY = os.getenv("ODDS_API_KEY")
BASE_URL = "https://api.the-odds-api.com/v4/sports/soccer_epl/odds"

history = {}
WINDOW = 600  # 10 perc


def calculate_center(line, over, under):
    if not over or not under:
        return None

    p_over = 1 / over
    p_under = 1 / under
    total = p_over + p_under
    p_norm = p_over / total

    center = line + (p_norm - 0.5)
    return round(center, 4)


def calculate_signal(delta):
    if delta is None:
        return {"signal": "NONE", "confidence": 0, "direction": "NEUTRAL"}

    if delta > 0.05:
        return {"signal": "STRONG", "confidence": 85, "direction": "OVER"}

    if delta < -0.05:
        return {"signal": "STRONG", "confidence": 85, "direction": "UNDER"}

    if abs(delta) > 0.02:
        return {"signal": "MEDIUM", "confidence": 70, "direction": "NEUTRAL"}

    return {"signal": "WEAK", "confidence": 60, "direction": "NEUTRAL"}


@app.get("/status")
def status():
    return {"system": "TRADE MAX PRO", "status": "running"}


@app.get("/matches")
async def matches():

    if not API_KEY:
        return {"error": "ODDS_API_KEY not set"}

    params = {
        "apiKey": API_KEY,
        "regions": "eu",
        "markets": "totals",
        "oddsFormat": "decimal"
    }

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(BASE_URL, params=params)

        if response.status_code != 200:
            return {"error": f"API error {response.status_code}"}

        data = response.json()

    now = time.time()
    results = []
    shortlist = []

    for match in data:

        home = match.get("home_team")
        away = match.get("away_team")
        start = match.get("commence_time")

        goal_over = None
        goal_under = None

        bookmakers = match.get("bookmakers", [])
        if bookmakers:
            markets = bookmakers[0].get("markets", [])
            for m in markets:
                if m.get("key") == "totals":
                    for outcome in m.get("outcomes", []):
                        if outcome.get("name") == "Over 2.5":
                            goal_over = outcome.get("price")
                        if outcome.get("name") == "Under 2.5":
                            goal_under = outcome.get("price")

        if not goal_over or not goal_under:
            continue

        # kis random mozgás teszteléshez
        move = random.uniform(-0.05, 0.05)
        goal_over = round(max(1.2, goal_over + move), 2)

        center = calculate_center(2.5, goal_over, goal_under)

        match_id = match.get("id")

        if match_id not in history:
            history[match_id] = []

        history[match_id].append({
            "time": now,
            "center": center
        })

        history[match_id] = [
            h for h in history[match_id]
            if now - h["time"] <= WINDOW
        ]

        delta = None
        if len(history[match_id]) > 1:
            delta = round(center - history[match_id][0]["center"], 4)

        signal = calculate_signal(delta)

        if abs(delta or 0) > 0.02:
            shortlist.append(match_id)

        results.append({
            "match_id": match_id,
            "home": home,
            "away": away,
            "start": start,
            "center": center,
            "delta": delta,
            "signal": signal
        })

    return {
        "shortlist": shortlist,
        "matches": results
    }
