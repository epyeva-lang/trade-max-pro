def calculate_goal_center(goal_data):

    over = goal_data.get("over")
    under = goal_data.get("under")
    line = goal_data.get("line")

    if over is None or under is None:
        return None

    try:
        p_over = 1 / over
        p_under = 1 / under
    except ZeroDivisionError:
        return None

    total_p = p_over + p_under

    if total_p == 0:
        return None

    p_norm = p_over / total_p

    center = line + (p_norm - 0.5)

    return {
        "p_over": round(p_over, 4),
        "p_under": round(p_under, 4),
        "p_norm": round(p_norm, 4),
        "center": round(center, 4)
    }
