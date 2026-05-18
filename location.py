# ============================================================
#  screens/location.py  --  Real Map + Live Location
# ============================================================

from kivymd.uix.screen    import MDScreen
from kivymd.uix.label     import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.snackbar  import Snackbar
from kivy.clock           import Clock
from kivy.metrics         import dp
from kivymd.app           import MDApp

from backend.location_service import (
    fetch_location_async,
    save_location_to_db,
    get_location_history,
    get_current,
    format_time,
)

DEMO_CHILD_ID = 1


class LocationScreen(MDScreen):

    map_widget = None
    map_marker = None

    def on_enter(self):
        self.build_map()
        self.load_location()

    def build_map(self):
        try:
            from kivy_garden.mapview import MapView, MapMarker
            if self.map_widget:
                try:
                    self.ids.map_container.remove_widget(self.map_widget)
                except Exception:
                    pass
            loc = get_current()
            self.map_widget = MapView(
                zoom=14, lat=loc["latitude"],
                lon=loc["longitude"], size_hint=(1, 1),
            )
            self.map_marker = MapMarker(
                lat=loc["latitude"], lon=loc["longitude"]
            )
            self.map_widget.add_marker(self.map_marker)
            self.ids.map_container.add_widget(self.map_widget)

        except ImportError:
            box = MDBoxLayout(
                orientation="vertical", size_hint=(1, 1),
                md_bg_color=(0.851, 0.929, 0.851, 1),
            )
            box.add_widget(MDLabel(
                text="Run:  pip install kivy_garden.mapview",
                halign="center",
                theme_text_color="Custom",
                text_color=(0.1, 0.4, 0.1, 1),
                font_size="14sp",
            ))
            try:
                self.ids.map_container.add_widget(box)
            except Exception:
                pass

    def load_location(self):
        self._status("Fetching live location...")
        fetch_location_async(
            callback=lambda ok: Clock.schedule_once(
                lambda dt: self._on_loaded(ok)
            )
        )

    def _on_loaded(self, success):
        loc = get_current()
        if success:
            self._status(f"{loc['address']}  --  {loc['time']}")
            self._move_map(loc["latitude"], loc["longitude"])
            save_location_to_db(DEMO_CHILD_ID)
            try:
                self.ids.address_label.text = loc["address"]
                self.ids.coords_label.text  = (
                    f"{loc['latitude']:.4f} N  --  "
                    f"{loc['longitude']:.4f} E"
                )
                self.ids.time_label.text = f"Updated: {loc['time']}"
            except Exception:
                pass
            self._load_history()
        else:
            self._status("Location failed. Check internet connection.")

    def _move_map(self, lat, lon):
        try:
            from kivy_garden.mapview import MapMarker
            if self.map_widget:
                self.map_widget.center_on(lat, lon)
                if self.map_marker:
                    self.map_widget.remove_marker(self.map_marker)
                self.map_marker = MapMarker(lat=lat, lon=lon)
                self.map_widget.add_marker(self.map_marker)
        except Exception as e:
            print(f"[Map] {e}")

    def _status(self, text):
        try:
            self.ids.location_status.text = text
        except Exception:
            pass

    def _load_history(self):
        try:
            history   = get_location_history(DEMO_CHILD_ID)
            container = self.ids.history_container
            container.clear_widgets()
            if not history:
                container.add_widget(MDLabel(
                    text="No history yet. Refresh to start.",
                    theme_text_color="Custom",
                    text_color=(0.478, 0.561, 0.651, 1),
                    font_size="13sp",
                    size_hint_y=None, height=dp(40),
                ))
                return
            for entry in history[:8]:
                container.add_widget(
                    self._row(entry["address"],
                              format_time(entry["logged_at"]))
                )
        except Exception as e:
            print(f"[History] {e}")

    def _row(self, address, time_str):
        row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=dp(52), spacing=dp(12),
        )
        row.add_widget(MDLabel(
            text=">", theme_text_color="Custom",
            text_color=(0.424, 0.388, 1, 1),
            font_size="18sp", size_hint_x=None, width=dp(20),
        ))
        box = MDBoxLayout(orientation="vertical", spacing=dp(2))
        box.add_widget(MDLabel(
            text=address, font_size="13sp", bold=True,
            theme_text_color="Custom",
            text_color=(0.122, 0.227, 0.373, 1),
            size_hint_y=None, height=dp(22),
        ))
        box.add_widget(MDLabel(
            text=time_str, font_size="11sp",
            theme_text_color="Custom",
            text_color=(0.478, 0.561, 0.651, 1),
            size_hint_y=None, height=dp(18),
        ))
        row.add_widget(box)
        return row

    def refresh_location(self):
        Snackbar(
            text="Fetching live location...",
            snackbar_x="8dp", snackbar_y="8dp",
            size_hint_x=0.95,
        ).open()
        self.load_location()

    def go_back(self):
        MDApp.get_running_app().switch_screen(
            "parent_dashboard", direction="right"
        )

    def go_to(self, screen):
        MDApp.get_running_app().switch_screen(screen)