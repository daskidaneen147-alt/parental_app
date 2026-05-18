# ============================================================
#  screens/login.py  —  Login Screen
# ============================================================

from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from backend.auth import login_parent
from backend.database import initialize_db


class LoginScreen(MDScreen):
    """
    First screen the user sees.
    Has: Logo, Email field, Password field, Login button, Sign Up link.
    """

    def on_enter(self):
        """Called every time this screen becomes visible."""
        initialize_db()   # Make sure database tables exist

    def do_login(self):
        """
        Called when 'Login' button is pressed.
        Reads email/password fields, validates, navigates to dashboard.
        """
        email    = self.ids.email_field.text.strip()
        password = self.ids.password_field.text.strip()

        if not email or not password:
            self.ids.error_label.text = "Please fill in all fields."
            return

        result = login_parent(email, password)

        if result["success"]:
            self.ids.error_label.text = ""
            MDApp.get_running_app().switch_screen("parent_dashboard")
        else:
            self.ids.error_label.text = result["message"]

    def go_to_signup(self):
        MDApp.get_running_app().switch_screen("signup")

    def toggle_password(self):
        """Show/hide password characters."""
        field = self.ids.password_field
        field.password = not field.password