# ============================================================
#  screens/parent_dashboard.py  —  Parent's Main Dashboard
# ============================================================

from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from backend.auth import get_current_user, logout
from backend.monitor import get_all_children, get_child_status
from backend.notifications import get_unread_count, DEMO_ALERTS


class ParentDashboardScreen(MDScreen):

    def on_enter(self):
        """Refresh data every time we come to this screen."""
        user = get_current_user()
        # Update greeting label
        if self.ids.get("greeting_label"):
            name = user["name"] if user["name"] else "Parent"
            self.ids.greeting_label.text = f"Hello, {name} 👋"

        # In a real app: load children from DB
        # For demo we show static data in KV

    def go_to(self, screen):
        MDApp.get_running_app().switch_screen(screen)

    def do_logout(self):
        logout()
        MDApp.get_running_app().switch_screen("login", direction="right")