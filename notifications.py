# ============================================================
#  screens/notifications.py  --  Real-time Notifications
# ============================================================

from kivymd.uix.screen    import MDScreen
from kivymd.uix.label     import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card      import MDCard
from kivymd.uix.label     import MDIcon
from kivy.metrics         import dp
from kivymd.app           import MDApp

from backend.notification_manager import (
    get_all_notifications,
    get_unread_count,
    mark_all_read,
    send_notification,
    set_refresh_callback,
)


class NotificationsScreen(MDScreen):

    def on_enter(self):
        """Screen kholne pe notifications load karo."""
        set_refresh_callback(self.load_notifications)
        self._add_demo_notifications()
        self.load_notifications()

    def _add_demo_notifications(self):
        """Demo notifications -- sirf ek baar add karo."""
        notifs = get_all_notifications()
        if len(notifs) == 0:
            send_notification(
                title      = "Sara tried to open TikTok",
                message    = "App blocked automatically",
                notif_type = "danger",
                child_name = "Sara",
            )
            send_notification(
                title      = "Screen Time Warning",
                message    = "Ahmed used 80% of daily limit",
                notif_type = "warning",
                child_name = "Ahmed",
            )
            send_notification(
                title      = "Sara arrived at school safely",
                message    = "Safe zone entered at 8:30 AM",
                notif_type = "info",
                child_name = "Sara",
            )
            send_notification(
                title      = "New app installed: PUBG Mobile",
                message    = "High risk game detected on device",
                notif_type = "danger",
                child_name = "Ahmed",
            )
            send_notification(
                title      = "Late Night Phone Use!",
                message    = "Ahmed using phone at 11:30 PM",
                notif_type = "danger",
                child_name = "Ahmed",
            )

    def load_notifications(self):
        """Notification list refresh karo."""
        try:
            notifs    = get_all_notifications()
            container = self.ids.notif_container
            container.clear_widgets()

            # Badge update
            unread = get_unread_count()
            try:
                self.ids.notif_badge.text = (
                    f"{unread} Unread" if unread > 0 else "All Read"
                )
            except Exception:
                pass

            if not notifs:
                container.add_widget(MDLabel(
                    text             = "No notifications yet.",
                    halign           = "center",
                    theme_text_color = "Custom",
                    text_color       = (0.478, 0.561, 0.651, 1),
                    font_size        = "14sp",
                    size_hint_y      = None,
                    height           = dp(60),
                ))
                return

            for notif in notifs:
                card = self._make_card(notif)
                container.add_widget(card)

        except Exception as e:
            print(f"[Notifications] Error: {e}")

    def _make_card(self, notif: dict):
        """Ek notification card banao."""
        ntype = notif.get("type", "info")

        # Colors
        if ntype == "danger":
            bg     = (1, 0.950, 0.950, 1)
            ic_col = (1, 0.298, 0.298, 1)
            icon   = "alert-circle"
            badge  = "DANGER"
        elif ntype == "warning":
            bg     = (1, 0.984, 0.930, 1)
            ic_col = (0.980, 0.600, 0.100, 1)
            icon   = "clock-alert-outline"
            badge  = "WARNING"
        else:
            bg     = (1, 1, 1, 1)
            ic_col = (0.298, 0.686, 0.314, 1)
            icon   = "check-circle-outline"
            badge  = "INFO"

        # Card
        card = MDCard(
            size_hint_y = None,
            height      = dp(105),
            md_bg_color = bg,
            radius      = [16, 16, 16, 16],
            elevation   = 2,
            padding     = dp(14),
        )

        outer = MDBoxLayout(
            orientation = "horizontal",
            spacing     = dp(12),
        )

        # Icon circle
        ic_card = MDCard(
            size_hint   = (None, None),
            size        = (dp(44), dp(44)),
            radius      = [22, 22, 22, 22],
            md_bg_color = (ic_col[0], ic_col[1], ic_col[2], 0.15),
        )
        ic_card.add_widget(MDIcon(
            icon             = icon,
            theme_text_color = "Custom",
            text_color       = ic_col,
            font_size        = "26sp",
            halign           = "center",
        ))

        # Text area
        txt = MDBoxLayout(
            orientation = "vertical",
            spacing     = dp(3),
        )

        txt.add_widget(MDLabel(
            text             = notif.get("title", ""),
            font_size        = "14sp",
            bold             = True,
            theme_text_color = "Custom",
            text_color       = (0.122, 0.227, 0.373, 1),
            size_hint_y      = None,
            height           = dp(24),
        ))

        txt.add_widget(MDLabel(
            text             = notif.get("message", ""),
            font_size        = "12sp",
            theme_text_color = "Custom",
            text_color       = (0.478, 0.561, 0.651, 1),
            size_hint_y      = None,
            height           = dp(20),
        ))

        # Bottom row: badge + time
        bottom = MDBoxLayout(
            adaptive_height = True,
            spacing         = dp(8),
        )

        badge_card = MDCard(
            size_hint_y  = None,
            height       = dp(20),
            size_hint_x  = None,
            width        = dp(70),
            md_bg_color  = (ic_col[0], ic_col[1], ic_col[2], 0.12),
            radius       = [10, 10, 10, 10],
            padding      = [dp(4), dp(2)],
        )
        badge_card.add_widget(MDLabel(
            text             = badge,
            theme_text_color = "Custom",
            text_color       = ic_col,
            font_size        = "9sp",
            bold             = True,
            halign           = "center",
        ))

        bottom.add_widget(badge_card)
        bottom.add_widget(MDLabel(
            text             = notif.get("time", ""),
            font_size        = "11sp",
            halign           = "right",
            theme_text_color = "Custom",
            text_color       = (0.478, 0.561, 0.651, 1),
            size_hint_y      = None,
            height           = dp(20),
        ))

        txt.add_widget(bottom)
        outer.add_widget(ic_card)
        outer.add_widget(txt)
        card.add_widget(outer)

        return card

    def clear_all(self):
        mark_all_read()
        self.load_notifications()

    def go_back(self):
        MDApp.get_running_app().switch_screen(
            "parent_dashboard", direction="right"
        )

    def go_to(self, screen):
        MDApp.get_running_app().switch_screen(screen)