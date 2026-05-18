# ============================================================
#  backend/security.py  —  App blocking & security checks
# ============================================================

from backend.database import fetch_all, execute_query, fetch_one


def block_app(child_id: int, app_name: str, package: str = "") -> dict:
    """Block an app for a specific child."""
    # Check if already blocked
    existing = fetch_one(
        "SELECT id FROM blocked_apps WHERE child_id=? AND app_name=?",
        (child_id, app_name)
    )
    if existing:
        return {"success": False, "message": f"{app_name} is already blocked."}

    execute_query(
        "INSERT INTO blocked_apps (child_id, app_name, package) VALUES (?,?,?)",
        (child_id, app_name, package)
    )
    return {"success": True, "message": f"{app_name} has been blocked!"}


def unblock_app(child_id: int, app_name: str) -> dict:
    """Remove an app from the blocked list."""
    execute_query(
        "DELETE FROM blocked_apps WHERE child_id=? AND app_name=?",
        (child_id, app_name)
    )
    return {"success": True, "message": f"{app_name} is now unblocked."}


def get_blocked_apps(child_id: int) -> list:
    """Return all blocked apps for a child."""
    return fetch_all(
        "SELECT * FROM blocked_apps WHERE child_id=? ORDER BY blocked_at DESC",
        (child_id,)
    )


def set_daily_limit(child_id: int, minutes: int) -> dict:
    """Set how many minutes per day a child can use the device."""
    if minutes < 0 or minutes > 1440:   # 1440 = 24 hours
        return {"success": False, "message": "Invalid time limit."}
    execute_query(
        "UPDATE children SET daily_limit=? WHERE id=?",
        (minutes, child_id)
    )
    return {"success": True, "message": f"Daily limit set to {minutes} minutes."}


def get_daily_limit(child_id: int) -> int:
    """Return daily screen-time limit for a child (in minutes)."""
    row = fetch_one("SELECT daily_limit FROM children WHERE id=?", (child_id,))
    return row["daily_limit"] if row else 120


# ── Dangerous app categories (for auto-suggestions) ────────
RISKY_APPS = [
    {"name": "TikTok",      "package": "com.zhiliaoapp.musically", "risk": "high"},
    {"name": "Instagram",   "package": "com.instagram.android",    "risk": "medium"},
    {"name": "Snapchat",    "package": "com.snapchat.android",     "risk": "medium"},
    {"name": "YouTube",     "package": "com.google.android.youtube","risk": "medium"},
    {"name": "Facebook",    "package": "com.facebook.katana",      "risk": "medium"},
    {"name": "Discord",     "package": "com.discord",              "risk": "high"},
    {"name": "WhatsApp",    "package": "com.whatsapp",             "risk": "low"},
    {"name": "Roblox",      "package": "com.roblox.client",        "risk": "medium"},
    {"name": "PUBG",        "package": "com.tencent.ig",           "risk": "high"},
    {"name": "Free Fire",   "package": "com.dts.freefireth",       "risk": "high"},
]


def get_risky_apps() -> list:
    """Return list of potentially risky apps parents should know about."""
    return RISKY_APPS