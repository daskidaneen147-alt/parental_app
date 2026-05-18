# ============================================================
#  backend/schedule.py  --  Smart Schedule System
#
#  4 Time Slots:
#    School Time  --> Sab apps band
#    Break Time   --> Sirf allowed apps (WhatsApp etc)
#    Home Time    --> Sab allowed
#    Sleep Time   --> Sab band
# ============================================================

from datetime import datetime, time
from backend.database import execute_query, fetch_all, fetch_one

# ── Default Schedule ────────────────────────────────────────
DEFAULT_SCHEDULE = {
    "school": {
        "name":          "School Time",
        "start":         "08:00",
        "end":           "14:00",
        "allowed_apps":  [],           # Koi app allowed nahi
        "blocked_all":   True,
        "icon":          "school-outline",
        "color":         (1, 0.298, 0.298, 1),   # Red
    },
    "break": {
        "name":          "Break Time",
        "start":         "14:00",
        "end":           "15:00",
        "allowed_apps":  ["WhatsApp", "SMS"],     # Sirf yeh
        "blocked_all":   False,
        "icon":          "coffee-outline",
        "color":         (0.980, 0.600, 0.100, 1),  # Orange
    },
    "home": {
        "name":          "Home Time",
        "start":         "15:00",
        "end":           "22:00",
        "allowed_apps":  [],           # Sab allowed
        "blocked_all":   False,
        "icon":          "home-outline",
        "color":         (0.298, 0.686, 0.314, 1),  # Green
    },
    "sleep": {
        "name":          "Sleep Time",
        "start":         "22:00",
        "end":           "08:00",
        "allowed_apps":  [],           # Koi app allowed nahi
        "blocked_all":   True,
        "icon":          "sleep",
        "color":         (0.424, 0.388, 1, 1),   # Purple
    },
}


def get_current_slot() -> dict:
    """
    Abhi ka time dekho aur bolo kaunsa slot chal raha hai.
    Returns slot dict with name, allowed_apps, etc.
    """
    now        = datetime.now().time()
    now_str    = now.strftime("%H:%M")

    for slot_key, slot in DEFAULT_SCHEDULE.items():
        start = slot["start"]
        end   = slot["end"]

        # Sleep slot midnight cross karta hai
        if start > end:
            # e.g. 22:00 to 08:00
            if now_str >= start or now_str < end:
                return {**slot, "key": slot_key}
        else:
            if start <= now_str < end:
                return {**slot, "key": slot_key}

    # Koi match nahi -- home default
    return {**DEFAULT_SCHEDULE["home"], "key": "home"}


def is_app_allowed(app_name: str) -> bool:
    """
    Check karo -- kya yeh app abhi allowed hai?
    Current slot ke hisaab se.
    """
    slot = get_current_slot()

    # Agar sab band hain
    if slot["blocked_all"]:
        # Sirf allowed_apps mein jo hain woh chal sakte hain
        if slot["allowed_apps"]:
            return app_name in slot["allowed_apps"]
        return False

    # Home time -- sab allowed
    return True


def get_schedule_status() -> dict:
    """
    Dashboard ke liye complete status return karo.
    """
    slot     = get_current_slot()
    now_time = datetime.now().strftime("%I:%M %p")

    return {
        "current_slot":    slot["name"],
        "slot_key":        slot["key"],
        "current_time":    now_time,
        "blocked_all":     slot["blocked_all"],
        "allowed_apps":    slot["allowed_apps"],
        "icon":            slot["icon"],
        "color":           slot["color"],
        "next_slot":       get_next_slot(slot["key"]),
        "next_slot_time":  slot["end"],
    }


def get_next_slot(current_key: str) -> str:
    """Next slot ka naam batao."""
    order = ["school", "break", "home", "sleep"]
    idx   = order.index(current_key) if current_key in order else 0
    next_idx = (idx + 1) % len(order)
    return DEFAULT_SCHEDULE[order[next_idx]]["name"]


def get_all_slots() -> dict:
    """Sare slots return karo -- Settings screen ke liye."""
    return DEFAULT_SCHEDULE


def update_slot_time(slot_key: str, start: str, end: str):
    """
    Slot ka time update karo.
    start/end format: "HH:MM"  e.g. "08:00"
    """
    if slot_key in DEFAULT_SCHEDULE:
        DEFAULT_SCHEDULE[slot_key]["start"] = start
        DEFAULT_SCHEDULE[slot_key]["end"]   = end
        print(f"[Schedule] {slot_key} updated: {start} - {end}")


def update_allowed_apps(slot_key: str, apps: list):
    """Slot ke allowed apps update karo."""
    if slot_key in DEFAULT_SCHEDULE:
        DEFAULT_SCHEDULE[slot_key]["allowed_apps"] = apps
        print(f"[Schedule] {slot_key} allowed: {apps}")


def get_time_remaining() -> str:
    """
    Current slot kab khatam hoga -- countdown.
    """
    slot      = get_current_slot()
    end_str   = slot["end"]
    now       = datetime.now()

    try:
        end_time  = datetime.strptime(end_str, "%H:%M").replace(
            year=now.year, month=now.month, day=now.day
        )
        if end_time < now:
            # Agle din ka end time
            from datetime import timedelta
            end_time += timedelta(days=1)

        diff      = end_time - now
        hours     = int(diff.seconds // 3600)
        minutes   = int((diff.seconds % 3600) // 60)

        if hours > 0:
            return f"{hours}h {minutes}m remaining"
        else:
            return f"{minutes} min remaining"
    except Exception:
        return ""