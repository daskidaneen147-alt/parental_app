# ============================================================
#  backend/monitor.py  —  Screen time tracking & child status
# ============================================================

from datetime import date
from backend.database import fetch_all, fetch_one, execute_query


def log_screen_time(child_id: int, minutes: int):
    """Add screen time for today."""
    today = str(date.today())
    existing = fetch_one(
        "SELECT id, minutes FROM screen_time_logs WHERE child_id=? AND date=?",
        (child_id, today)
    )
    if existing:
        new_total = existing["minutes"] + minutes
        execute_query(
            "UPDATE screen_time_logs SET minutes=? WHERE id=?",
            (new_total, existing["id"])
        )
    else:
        execute_query(
            "INSERT INTO screen_time_logs (child_id, date, minutes) VALUES (?,?,?)",
            (child_id, today, minutes)
        )


def get_today_screen_time(child_id: int) -> int:
    """Return how many minutes screen was used today."""
    today = str(date.today())
    row = fetch_one(
        "SELECT minutes FROM screen_time_logs WHERE child_id=? AND date=?",
        (child_id, today)
    )
    return row["minutes"] if row else 0


def get_weekly_screen_time(child_id: int) -> list:
    """Return last 7 days of screen time as a list of dicts."""
    return fetch_all(
        """SELECT date, minutes FROM screen_time_logs
           WHERE child_id=? ORDER BY date DESC LIMIT 7""",
        (child_id,)
    )


def get_all_children(parent_id: int) -> list:
    """Return all children profiles for a parent."""
    return fetch_all(
        "SELECT * FROM children WHERE parent_id=? ORDER BY name",
        (parent_id,)
    )


def add_child(parent_id: int, name: str, age: int) -> dict:
    """Add a new child profile."""
    if not name.strip():
        return {"success": False, "message": "Name cannot be empty."}
    child_id = execute_query(
        "INSERT INTO children (parent_id, name, age) VALUES (?,?,?)",
        (parent_id, name, age)
    )
    return {"success": True, "child_id": child_id, "message": f"{name} added!"}


def get_child_status(child_id: int) -> dict:
    """
    Return a summary card for one child:
    name, online status, today's screen time, daily limit.
    """
    child    = fetch_one("SELECT * FROM children WHERE id=?", (child_id,))
    used     = get_today_screen_time(child_id)
    limit    = child["daily_limit"] if child else 120
    percent  = min(int((used / limit) * 100), 100) if limit else 0

    return {
        "name":         child["name"]      if child else "Unknown",
        "age":          child["age"]       if child else 0,
        "is_online":    bool(child["is_online"]) if child else False,
        "used_minutes": used,
        "limit_minutes":limit,
        "percent_used": percent,
    }