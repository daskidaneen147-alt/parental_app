# ============================================================
#  screens/app_block.py
#  Features:
#    1. Switch toggle pe color change (red=blocked, green=allowed)
#    2. Blocked apps count real-time update
#    3. Snackbar alert jab block/unblock ho
# ============================================================

from kivymd.uix.screen   import MDScreen
from kivymd.uix.snackbar import Snackbar
from kivymd.app          import MDApp
from backend.database    import execute_query, fetch_all

DEMO_CHILD_ID = 1

# ── In-memory blocked apps tracker ─────────────────────────
# Key = app name, Value = True (blocked) / False (allowed)
APPS_STATUS = {
    "TikTok":    True,
    "Instagram": True,
    "Snapchat":  False,
    "PUBG":      True,
    "Free Fire": False,
    "YouTube":   False,
}


def get_blocked_count() -> int:
    """Kitni apps block hain abhi."""
    return sum(1 for v in APPS_STATUS.values() if v)


class AppBlockScreen(MDScreen):

    def on_enter(self):
        """Screen kھulne pe count update karo."""
        self.update_count()

    def update_count(self):
        """Header mein blocked count update karo."""
        count = get_blocked_count()
        try:
            self.ids.blocked_count_label.text = f"{count} Blocked"
        except Exception:
            pass

    def toggle_app(self, app_name: str, is_active: bool):
        """
        Switch dabane pe:
        1. Status update karo
        2. Color change karo
        3. Alert dikhao
        4. Count update karo
        5. Database mein save karo
        """
        # Status update
        APPS_STATUS[app_name] = is_active

        # Alert message
        if is_active:
            msg   = f"{app_name} has been BLOCKED!"
            color = (1, 0.298, 0.298, 1)   # Red
        else:
            msg   = f"{app_name} has been UNBLOCKED!"
            color = (0.298, 0.686, 0.314, 1)  # Green

        # Snackbar alert
        Snackbar(
            text        = msg,
            snackbar_x  = "8dp",
            snackbar_y  = "8dp",
            size_hint_x = 0.95,
        ).open()

        # Count update karo
        self.update_count()

        # Database mein save karo
        self._save_to_db(app_name, is_active)

        print(f"[AppBlock] {app_name}: {'BLOCKED' if is_active else 'ALLOWED'}")

    def _save_to_db(self, app_name: str, is_blocked: bool):
        """Block/unblock database mein save karo."""
        try:
            if is_blocked:
                # Pehle check karo already hai ya nahi
                existing = fetch_all(
                    "SELECT id FROM blocked_apps WHERE child_id=? AND app_name=?",
                    (DEMO_CHILD_ID, app_name)
                )
                if not existing:
                    execute_query(
                        "INSERT INTO blocked_apps (child_id, app_name) VALUES (?,?)",
                        (DEMO_CHILD_ID, app_name)
                    )
            else:
                execute_query(
                    "DELETE FROM blocked_apps WHERE child_id=? AND app_name=?",
                    (DEMO_CHILD_ID, app_name)
                )
        except Exception as e:
            print(f"[AppBlock] DB error: {e}")

    def go_back(self):
        MDApp.get_running_app().switch_screen(
            "parent_dashboard", direction="right"
        )

    def go_to(self, screen):
        MDApp.get_running_app().switch_screen(screen)