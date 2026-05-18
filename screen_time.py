# ============================================================
#  screens/screen_time.py  —  Screen Time Control
# ============================================================
from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivymd.uix.snackbar import Snackbar
from backend.security import set_daily_limit, get_daily_limit

DEMO_CHILD_ID = 1


class ScreenTimeScreen(MDScreen):

    def on_enter(self):
        limit = get_daily_limit(DEMO_CHILD_ID)
        if self.ids.get("limit_label"):
            self.ids.limit_label.text = f"{limit} min / day"

    def set_limit(self, minutes):
        result = set_daily_limit(DEMO_CHILD_ID, int(minutes))
        Snackbar(text=result["message"], snackbar_x="8dp",
                 snackbar_y="8dp", size_hint_x=0.95).open()
        if self.ids.get("limit_label"):
            self.ids.limit_label.text = f"{int(minutes)} min / day"

    def go_back(self):
        MDApp.get_running_app().switch_screen("parent_dashboard", direction="right")

    def go_to(self, screen):
        MDApp.get_running_app().switch_screen(screen)