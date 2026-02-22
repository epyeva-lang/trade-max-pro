def analyze_combined(corner, goal, btts):
    if corner["confidence"] > 70 and goal["confidence"] > 70:
        return {
            "market": "combined",
            "signal": "strong",
            "confidence": 90
        }
    return {
        "market": "combined",
        "signal": "none",
        "confidence": 0
    }
