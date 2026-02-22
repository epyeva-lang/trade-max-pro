from datetime import datetime


def extract_totals(markets, target_line):

    over = None
    under = None

    for m in markets:
        if m.get("key") == "totals":
            for outcome in m.get("outcomes", []):
                if outcome.get("point") == target_line:
                    if outcome.get("name") == "Over":
                        over = outcome.get("price")
                    elif outcome.get("name") == "Under":
                        under = outcome.get("price")

    return over, under


def parse_match(match):

    if not match.get("bookmakers"):
        return None

    bookmaker = match["bookmakers"][0]
    markets = bookmaker.get("markets", [])

    goal_over_25, goal_under_25 = extract_totals(markets, 2.5)
    goal_over_35, goal_under_35 = extract_totals(markets, 3.5)

    corner_lines = [8.5, 9.5, 10.5]
    corner_data = []

    for line in corner_lines:
        over, under = extract_totals(markets, line)

        if over is not None and under is not None:
            spread = abs((1 / over) - (1 / under))
            corner_data.append((line, over, under, spread))

    corner_line = None
    corner_over = None
    corner_under = None

    if corner_data:
        corner_data.sort(key=lambda x: x[3])
        corner_line, corner_over, corner_under, _ = corner_data[0]

    return {
        "match_id": match.get("id"),
        "timestamp": datetime.utcnow().isoformat(),
        "goal": {
            "line": 2.5,
            "over": goal_over_25,
            "under": goal_under_25
        },
        "goal_alt": {
            "line": 3.5,
            "over": goal_over_35,
            "under": goal_under_35
        },
        "corner": {
            "line": corner_line,
            "over": corner_over,
            "under": corner_under
        }
    }
