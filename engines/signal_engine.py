def calculate_signal(match):

    goal = match.get("goal")
    center_data = match.get("goal_center")
    delta = match.get("goal_delta_10m")

    if not goal or not center_data or delta is None:
        return {
            "signal": "NONE",
            "confidence": 0,
            "direction": "NEUTRAL"
        }

    over = goal.get("over")
    under = goal.get("under")

    if over is None or under is None:
        return {
            "signal": "NONE",
            "confidence": 0,
            "direction": "NEUTRAL"
        }

    # Spread számítás
    p_over = 1 / over
    p_under = 1 / under
    spread = abs(p_over - p_under)

    score = 60

    # Delta alapú pontok
    if abs(delta) > 0.05:
        score += 10

    if abs(delta) > 0.08:
        score += 10

    # Spread bónusz
    if spread < 0.06:
        score += 10

    # Center torzulás irányba
    center = center_data.get("center")
    if delta > 0 and center > 2.53:
        score += 10
    elif delta < 0 and center < 2.47:
        score += 10

    # Max 100
    score = min(score, 100)

    # Irány
    if delta > 0.05:
        direction = "OVER"
    elif delta < -0.05:
        direction = "UNDER"
    else:
        direction = "NEUTRAL"

    # Signal szint
    if score >= 80:
        signal = "STRONG"
    elif score >= 70:
        signal = "MEDIUM"
    else:
        signal = "WEAK"

    return {
        "signal": signal,
        "confidence": score,
        "direction": direction
    }
