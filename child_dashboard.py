# ============================================================
#  screens/child_dashboard.py
# ============================================================
from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp

class ChildDashboardScreen(MDScreen):
    def go_back(self):
        MDApp.get_running_app().switch_screen("parent_dashboard", direction="right")

    def go_to(self, screen):
        MDApp.get_running_app().switch_screen(screen)