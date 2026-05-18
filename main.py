# ============================================================
#  main.py  --  GuardianEye Parental Control App
#  Version: 2.0
#  Compatible: Windows (PC) + Android (APK)
# ============================================================

import os
import platform
import os
import sys

# Android pe kv file ka path fix
if 'ANDROID_ARGUMENT' in os.environ:
    from android.storage import app_storage_path
    os.chdir(app_storage_path())
    
# ── Android / PC Detection ─────────────────────────────────
IS_ANDROID = (
    "ANDROID_ARGUMENT" in os.environ or
    "ANDROID_ROOT"     in os.environ
)

# ── Environment fixes ──────────────────────────────────────
os.environ["KIVY_NO_CONSOLELOG"] = "1"

# Android + Linux pe xsel nahi hota
if IS_ANDROID or platform.system() == "Linux":
    os.environ["KIVY_CLIPBOARD"] = "dummy"

# ── Window size (sirf PC pe) ───────────────────────────────
from kivy.config import Config
if not IS_ANDROID:
    Config.set("graphics", "width",    "400")
    Config.set("graphics", "height",   "780")
    Config.set("graphics", "resizable","0")

# ── Core imports ───────────────────────────────────────────
from kivymd.app             import MDApp
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.lang              import Builder

print("=" * 50)
print("  GuardianEye v2.0 Starting...")
print(f"  Platform: {'Android' if IS_ANDROID else platform.system()}")
print("=" * 50)

# ── Backend imports ────────────────────────────────────────
DB_OK       = False
LOCATION_OK = False
NOTIF_OK    = False
FIREBASE_OK = False
GPS_OK      = False

try:
    from backend.database import initialize_db
    DB_OK = True
    print("[OK] database")
except Exception as e:
    print(f"[SKIP] database: {e}")

try:
    from backend.location_service import fetch_location_async
    LOCATION_OK = True
    print("[OK] location_service")
except Exception as e:
    print(f"[SKIP] location_service: {e}")

try:
    from backend.notification_manager import start_background_monitor
    NOTIF_OK = True
    print("[OK] notification_manager")
except Exception as e:
    print(f"[SKIP] notification_manager: {e}")

try:
    from backend.firebase_service import initialize_firebase
    FIREBASE_OK = True
    print("[OK] firebase_service")
except Exception as e:
    print(f"[SKIP] firebase_service: {e}")

try:
    from backend.gps_tracker import start_tracking, stop_gps
    GPS_OK = True
    print("[OK] gps_tracker")
except Exception as e:
    print(f"[SKIP] gps_tracker: {e}")

# ── Screen imports ─────────────────────────────────────────
SplashScreen          = None
LoginScreen           = None
SignupScreen          = None
ParentDashboardScreen = None
ChildDashboardScreen  = None
AppBlockScreen        = None
ScreenTimeScreen      = None
LocationScreen        = None
NotificationsScreen   = None
SettingsScreen        = None
SmartScheduleScreen   = None

try:
    from screens.splash import SplashScreen
    print("[OK] SplashScreen")
except Exception as e:
    print(f"[SKIP] SplashScreen: {e}")

try:
    from screens.login import LoginScreen
    print("[OK] LoginScreen")
except Exception as e:
    print(f"[SKIP] LoginScreen: {e}")

try:
    from screens.signup import SignupScreen
    print("[OK] SignupScreen")
except Exception as e:
    print(f"[SKIP] SignupScreen: {e}")

try:
    from screens.parent_dashboard import ParentDashboardScreen
    print("[OK] ParentDashboardScreen")
except Exception as e:
    print(f"[SKIP] ParentDashboardScreen: {e}")

try:
    from screens.child_dashboard import ChildDashboardScreen
    print("[OK] ChildDashboardScreen")
except Exception as e:
    print(f"[SKIP] ChildDashboardScreen: {e}")

try:
    from screens.app_block import AppBlockScreen
    print("[OK] AppBlockScreen")
except Exception as e:
    print(f"[SKIP] AppBlockScreen: {e}")

try:
    from screens.screen_time import ScreenTimeScreen
    print("[OK] ScreenTimeScreen")
except Exception as e:
    print(f"[SKIP] ScreenTimeScreen: {e}")

try:
    from screens.location import LocationScreen
    print("[OK] LocationScreen")
except Exception as e:
    print(f"[SKIP] LocationScreen: {e}")

try:
    from screens.notifications import NotificationsScreen
    print("[OK] NotificationsScreen")
except Exception as e:
    print(f"[SKIP] NotificationsScreen: {e}")

try:
    from screens.settings import SettingsScreen
    print("[OK] SettingsScreen")
except Exception as e:
    print(f"[SKIP] SettingsScreen: {e}")

try:
    from screens.smart_schedule import SmartScheduleScreen
    print("[OK] SmartScheduleScreen")
except Exception as e:
    print(f"[SKIP] SmartScheduleScreen: {e}")

# ── Load KV file ───────────────────────────────────────────
try:
    Builder.load_file("parental.kv")
    print("[OK] parental.kv loaded")
except Exception as e:
    print(f"[ERROR] parental.kv: {e}")


# ============================================================
#  MAIN APP
# ============================================================
class GuardianEyeApp(MDApp):

    def build(self):
        print("[App] Building...")

        # Theme
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue     = "900"
        self.theme_cls.accent_palette  = "DeepPurple"
        self.theme_cls.theme_style     = "Light"

        # Database
        if DB_OK:
            try:
                initialize_db()
                print("[App] DB ready")
            except Exception as e:
                print(f"[App] DB error: {e}")

        # Firebase
        if FIREBASE_OK:
            try:
                initialize_firebase()
                print("[App] Firebase ready")
            except Exception as e:
                print(f"[App] Firebase error: {e}")

        # Location
        if LOCATION_OK:
            try:
                fetch_location_async()
                print("[App] Location started")
            except Exception as e:
                print(f"[App] Location error: {e}")

        # GPS
        if GPS_OK:
            try:
                start_tracking()
                print("[App] GPS started")
            except Exception as e:
                print(f"[App] GPS error: {e}")

        # Background monitor
        if NOTIF_OK:
            try:
                start_background_monitor()
                print("[App] Monitor started")
            except Exception as e:
                print(f"[App] Monitor error: {e}")

        # Screen Manager
        sm = ScreenManager(transition=SlideTransition())

        screens = [
            ("splash",           SplashScreen),
            ("login",            LoginScreen),
            ("signup",           SignupScreen),
            ("parent_dashboard", ParentDashboardScreen),
            ("child_dashboard",  ChildDashboardScreen),
            ("app_block",        AppBlockScreen),
            ("screen_time",      ScreenTimeScreen),
            ("location",         LocationScreen),
            ("notifications",    NotificationsScreen),
            ("settings",         SettingsScreen),
            ("smart_schedule",   SmartScheduleScreen),
        ]

        for name, ScreenClass in screens:
            if ScreenClass is not None:
                try:
                    sm.add_widget(ScreenClass(name=name))
                    print(f"[App] Screen added: {name}")
                except Exception as e:
                    print(f"[App] Screen failed ({name}): {e}")

        print("[App] Build complete!")
        return sm

    def switch_screen(self, screen_name: str, direction: str = "left"):
        """Navigate to any screen."""
        try:
            self.root.transition.direction = direction
            self.root.current = screen_name
        except Exception as e:
            print(f"[Nav] Error: {e}")

    def on_pause(self):
        """Android: app pause pe True return karo."""
        return True

    def on_resume(self):
        """Android: app resume."""
        pass

    def on_stop(self):
        """App close hone pe cleanup."""
        if GPS_OK:
            try:
                stop_gps()
            except Exception:
                pass
        print("[App] GuardianEye closed.")


if __name__ == "__main__":
    GuardianEyeApp().run()