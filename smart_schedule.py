# ============================================================
#  screens/smart_schedule.py  --  Smart Schedule Screen
# ============================================================

from kivymd.uix.screen   import MDScreen
from kivymd.uix.snackbar import Snackbar
from kivymd.app          import MDApp
from kivy.clock          import Clock

from backend.schedule import (
    get_schedule_status,
    get_all_slots,
    update_slot_time,
    update_allowed_apps,
    get_time_remaining,
)


class SmartScheduleScreen(MDScreen):

    def on_enter(self):
        """Screen open hone pe status refresh karo."""
        self.refresh_status()
        # Har 60 second mein auto refresh
        Clock.schedule_interval(
            lambda dt: self.refresh_status(), 60
        )

    def on_leave(self):
        Clock.unschedule(self.refresh_status)

    def refresh_status(self):
        """Current slot status update karo."""
        try:
            status = get_schedule_status()

            # Current slot name
            self.ids.current_slot_label.text = (
                status["current_slot"]
            )

            # Current time
            self.ids.current_time_label.text = (
                status["current_time"]
            )

            # Status message
            if status["blocked_all"]:
                if status["allowed_apps"]:
                    apps = ", ".join(status["allowed_apps"])
                    self.ids.status_message.text = (
                        f"Only allowed: {apps}"
                    )
                else:
                    self.ids.status_message.text = (
                        "All apps are blocked"
                    )
            else:
                self.ids.status_message.text = (
                    "All apps are allowed"
                )

            # Time remaining
            self.ids.time_remaining.text = get_time_remaining()

            # Next slot
            self.ids.next_slot_label.text = (
                f"Next: {status['next_slot']} "
                f"at {status['next_slot_time']}"
            )

        except Exception as e:
            print(f"[Schedule] Refresh error: {e}")

    def save_schedule(self):
        """Schedule save karo."""
        try:
            # School time
            update_slot_time(
                "school",
                self.ids.school_start.text or "08:00",
                self.ids.school_end.text   or "14:00",
            )
            # Break time
            update_slot_time(
                "break",
                self.ids.break_start.text  or "14:00",
                self.ids.break_end.text    or "15:00",
            )
            # Home time
            update_slot_time(
                "home",
                self.ids.home_start.text   or "15:00",
                self.ids.home_end.text     or "22:00",
            )
            # Sleep time
            update_slot_time(
                "sleep",
                self.ids.sleep_start.text  or "22:00",
                self.ids.sleep_end.text    or "08:00",
            )

            # Break allowed apps
            apps_text = self.ids.break_apps.text.strip()
            if apps_text:
                apps = [a.strip() for a in apps_text.split(",")]
                update_allowed_apps("break", apps)

            self.refresh_status()

            Snackbar(
                text        = "Schedule saved successfully!",
                snackbar_x  = "8dp",
                snackbar_y  = "8dp",
                size_hint_x = 0.95,
            ).open()

        except Exception as e:
            print(f"[Schedule] Save error: {e}")

    def go_back(self):
        MDApp.get_running_app().switch_screen(
            "parent_dashboard", direction="right"
        )

    def go_to(self, screen):
        MDApp.get_running_app().switch_screen(screen)