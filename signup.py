# ============================================================
#  screens/signup.py  —  Sign Up Screen
# ============================================================

from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from backend.auth import signup_parent


class SignupScreen(MDScreen):

    def do_signup(self):
        name     = self.ids.name_field.text.strip()
        email    = self.ids.email_field.text.strip()
        password = self.ids.password_field.text.strip()
        confirm  = self.ids.confirm_field.text.strip()

        # Validate
        if not all([name, email, password, confirm]):
            self.ids.error_label.text = "All fields are required."
            return
        if password != confirm:
            self.ids.error_label.text = "Passwords do not match."
            return

        result = signup_parent(name, email, password)
        if result["success"]:
            self.ids.error_label.text = ""
            # Go back to login after successful signup
            MDApp.get_running_app().switch_screen("login", direction="right")
        else:
            self.ids.error_label.text = result["message"]

    def go_to_login(self):
        MDApp.get_running_app().switch_screen("login", direction="right")