# ============================================================
#  backend/notification_manager.py
#  Real-time notifications:
#    1. In-app (Snackbar + Notifications screen)
#    2. Windows desktop notifications (plyer)
#
#  Triggers:
#    - Location change
#    - App block attempt
#    - Screen time limit reached
#    - Late night phone use
# ============================================================

import threading
from datetime   import datetime
from kivy.clock import Clock

# ── Try desktop notifications ───────────────────────────────
try:
    from plyer import notification as desktop_notif
    DESKTOP_NOTIF_OK = True
    print("[Notif] Desktop notifications: OK")
except Exception:
    DESKTOP_NOTIF_OK = False
    print("[Notif] Desktop notifications: Not available")

# ── Database import ─────────────────────────────────────────
from backend.database import execute_query, fetch_all

# ── In-memory notification queue ───────────────────────────
# Yeh list Notifications screen mein dikhegi
notification_queue = []

# ── Callback function (screen refresh ke liye) ──────────────
_refresh_callback = None


def set_refresh_callback(callback):
    """
    Notifications screen apna refresh function register kare.
    Jab nai notification aaye, screen auto-refresh ho.
    """
    global _refresh_callback
    _refresh_callback = callback


# ── MAIN FUNCTION: Notification bhejo ──────────────────────
def send_notification(
    title:      str,
    message:    str,
    notif_type: str = "info",    # info | warning | danger
    child_name: str = "Sara",
    parent_id:  int = 1,
    child_id:   int = 1,
):
    """
    Notification bhejo:
    1. Windows desktop popup
    2. In-app queue mein add karo
    3. Database mein save karo
    4. Notifications screen refresh karo
    """
    now = datetime.now().strftime("%I:%M %p")

    # ── 1. Windows Desktop Notification ────────────────────
    if DESKTOP_NOTIF_OK:
        try:
            desktop_notif.notify(
                title       = f"GuardianEye -- {title}",
                message     = message,
                app_name    = "GuardianEye",
                timeout     = 6,   # 6 second dikhao
            )
        except Exception as e:
            print(f"[Notif] Desktop failed: {e}")

    # ── 2. In-app queue mein add karo ──────────────────────
    notif_entry = {
        "title":      title,
        "message":    message,
        "type":       notif_type,
        "child_name": child_name,
        "time":       now,
        "is_read":    False,
    }
    notification_queue.insert(0, notif_entry)   # Nai pehle

    # Max 50 notifications rakhain
    if len(notification_queue) > 50:
        notification_queue.pop()

    # ── 3. Database mein save karo ─────────────────────────
    try:
        execute_query(
            """INSERT INTO alerts
               (parent_id, child_id, message, alert_type, is_read)
               VALUES (?, ?, ?, ?, 0)""",
            (parent_id, child_id, f"{title}: {message}", notif_type)
        )
    except Exception as e:
        print(f"[Notif] DB save error: {e}")

    # ── 4. Screen refresh karo ─────────────────────────────
    if _refresh_callback:
        Clock.schedule_once(lambda dt: _refresh_callback(), 0)

    print(f"[Notif] {notif_type.upper()}: {title} -- {message}")


# ── LOCATION NOTIFICATION ───────────────────────────────────
def notify_location_change(child_name: str, location: str, is_safe: bool):
    """Jab bacha kisi jagah aaye ya jaye."""
    if is_safe:
        send_notification(
            title      = f"{child_name} -- Safe Location",
            message    = f"{child_name} arrived at {location}",
            notif_type = "info",
            child_name = child_name,
        )
    else:
        send_notification(
            title      = f"{child_name} -- Left Safe Zone!",
            message    = f"{child_name} left {location}. Current: Unknown area",
            notif_type = "danger",
            child_name = child_name,
        )


# ── APP BLOCK NOTIFICATION ──────────────────────────────────
def notify_app_blocked(child_name: str, app_name: str):
    """Jab bacha koi blocked app kholne ki koshish kare."""
    send_notification(
        title      = f"App Blocked!",
        message    = f"{child_name} tried to open {app_name}",
        notif_type = "danger",
        child_name = child_name,
    )


# ── SCREEN TIME NOTIFICATION ────────────────────────────────
def notify_screen_time(child_name: str, used_hours: float, limit_hours: float):
    """Jab screen time limit ke kareeb ya exceed ho."""
    percent = int((used_hours / limit_hours) * 100)

    if percent >= 100:
        send_notification(
            title      = "Screen Time Limit Reached!",
            message    = f"{child_name} used {used_hours:.1f}h of {limit_hours}h limit",
            notif_type = "danger",
            child_name = child_name,
        )
    elif percent >= 80:
        send_notification(
            title      = "Screen Time Warning",
            message    = f"{child_name} used {percent}% of daily limit",
            notif_type = "warning",
            child_name = child_name,
        )


# ── LATE NIGHT NOTIFICATION ─────────────────────────────────
def notify_late_night(child_name: str, current_time: str):
    """Jab bacha raat ko phone use kare."""
    send_notification(
        title      = "Late Night Phone Use!",
        message    = f"{child_name} is using phone at {current_time}",
        notif_type = "danger",
        child_name = child_name,
    )


# ── BACKGROUND MONITOR ──────────────────────────────────────
def start_background_monitor():
    """
    Background thread mein activities monitor karo.
    Har minute check karta hai.
    """
    def _monitor():
        import time
        print("[Monitor] Background monitoring started!")

        while True:
            try:
                _check_late_night()
                _check_screen_time()
            except Exception as e:
                print(f"[Monitor] Error: {e}")
            time.sleep(60)   # Har 60 second mein check

    thread = threading.Thread(target=_monitor, daemon=True)
    thread.start()


def _check_late_night():
    """Raat 10 PM ke baad phone use check karo."""
    now  = datetime.now()
    hour = now.hour

    # 10 PM se 6 AM = late night
    if hour >= 22 or hour < 6:
        time_str = now.strftime("%I:%M %p")
        # Sirf ek baar notify karo har ghante mein
        if now.minute == 0:
            notify_late_night("Sara", time_str)


def _check_screen_time():
    """Screen time limit check karo."""
    try:
        from backend.monitor import get_today_screen_time
        from backend.security import get_daily_limit

        used  = get_today_screen_time(child_id=1)
        limit = get_daily_limit(child_id=1)

        if limit > 0:
            notify_screen_time(
                child_name  = "Sara",
                used_hours  = used / 60,
                limit_hours = limit / 60,
            )
    except Exception:
        pass


# ── HELPER FUNCTIONS ────────────────────────────────────────
def get_all_notifications() -> list:
    """In-app queue se sari notifications lo."""
    return notification_queue


def get_unread_count() -> int:
    """Unread notifications count."""
    return sum(1 for n in notification_queue if not n["is_read"])


def mark_all_read():
    """Sab notifications read mark karo."""
    for n in notification_queue:
        n["is_read"] = True


def clear_all():
    """Sab notifications clear karo."""
    notification_queue.clear()