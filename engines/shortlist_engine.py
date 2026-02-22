SHORTLIST_STORE = {}

MAX_SHORTLIST_SIZE = 20


def calculate_spread(goal_data):

    over = goal_data.get("over")
    under = goal_data.get("under")

    if over is None or under is None:
        return None

    p_over = 1 / over
    p_under = 1 / under

    return abs(p_over - p_under)


def calculate_stability_score(match):

    goal = match.get("goal")
    center_data = match.get("goal_center")

    if not goal or not center_data:
        return None

    spread = calculate_spread(goal)
    if spread is None:
        return None

    center = center_data.get("center")
    if center is None:
        return None

    # Spread minél kisebb → annál jobb
    spread_score = 1 - spread

    # Center minél közelebb 2.5-höz → annál jobb
    center_distance = abs(center - 2.5)
    center_score = 1 - center_distance

    # Súlyozott kombináció
    score = (spread_score * 0.6) + (center_score * 0.4)

    return score


def build_shortlist(matches):

    scored_matches = []

    for match in matches:
        score = calculate_stability_score(match)
        if score is not None:
            scored_matches.append((match["match_id"], score))

    # Rangsorolás score alapján (legjobb elöl)
    scored_matches.sort(key=lambda x: x[1], reverse=True)

    # Top N kiválasztás
    top_matches = [m[0] for m in scored_matches[:MAX_SHORTLIST_SIZE]]

    global SHORTLIST_STORE
    SHORTLIST_STORE = {m: True for m in top_matches}

    return top_matches


def is_in_shortlist(match_id):
    return SHORTLIST_STORE.get(match_id, False)
