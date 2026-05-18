# ============================================================
#  screens/settings.py  —  Settings Screen
# ============================================================
from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivymd.uix.snackbar import Snackbar


class SettingsScreen(MDScreen):

    def save_settings(self):
        Snackbar(text="Settings saved successfully!",
                 snackbar_x="8dp", snackbar_y="8dp",
                 size_hint_x=0.95).open()

    def do_logout(self):
        from backend.auth import logout
        logout()
        MDApp.get_running_app().switch_screen("login", direction="right")

    def go_back(self):
        MDApp.get_running_app().switch_screen("parent_dashboard", direction="right")

    def go_to(self, screen):
        MDApp.get_running_app().switch_screen(screen)