from collections import defaultdict
from datetime import datetime, timedelta

# memória tároló
memory_store = defaultdict(list)

WINDOW_MINUTES = 10


def update_memory(match_id, center_value):

    now = datetime.utcnow()

    if center_value is None:
        return None

    memory_store[match_id].append((now, center_value))

    # Töröljük a 10 percnél régebbi adatokat
    cutoff = now - timedelta(minutes=WINDOW_MINUTES)

    memory_store[match_id] = [
        (ts, val)
        for ts, val in memory_store[match_id]
        if ts >= cutoff
    ]

    # Ha nincs elég adat → nincs delta
    if len(memory_store[match_id]) < 2:
        return None

    oldest_center = memory_store[match_id][0][1]
    current_center = memory_store[match_id][-1][1]

    delta = current_center - oldest_center

    return round(delta, 4)
