import os
import httpx
import random

API_KEY = os.getenv("ODDS_API_KEY")
BASE_URL = "https://api.the-odds-api.com/v4/sports/soccer_epl/odds"

SIMULATION_MODE = True


class OddsAdapter:

    async def fetch_soccer_matches(self):

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

        parsed = []

        for match in data:

            home = match.get("home_team")
            away = match.get("away_team")
            commence = match.get("commence_time")

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

            # Simulation
            if SIMULATION_MODE:
                move = random.uniform(-0.05, 0.05)
                goal_over = round(max(1.2, goal_over + move), 2)

            parsed.append({
                "match_id": match.get("id"),
                "home": home,
                "away": away,
                "start": commence,
                "goal": {
                    "line": 2.5,
                    "over": goal_over,
                    "under": goal_under
                }
            })

        return parsed
