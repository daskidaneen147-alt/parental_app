

# ============================================================
#  screens/splash.py  --  Animated Splash Screen
#  App start hone pe 3 second dikhega phir login pe jayega
# ============================================================
 
from kivymd.uix.screen import MDScreen
from kivy.animation    import Animation
from kivy.clock        import Clock
from kivymd.app        import MDApp
 
 
class SplashScreen(MDScreen):
 
    def on_enter(self):
        """Splash screen dikhne ke baad animation start karo."""
        # Logo fade in
        self.ids.logo_card.opacity  = 0
        self.ids.app_name.opacity   = 0
        self.ids.tagline.opacity    = 0
        self.ids.loading_bar.opacity = 0
 
        # Step 1: Logo aaye
        anim1 = Animation(opacity=1, duration=0.8)
        anim1.start(self.ids.logo_card)
 
        # Step 2: App name aaye
        Clock.schedule_once(self._show_name,    0.6)
        # Step 3: Tagline aaye
        Clock.schedule_once(self._show_tagline, 1.0)
        # Step 4: Loading bar
        Clock.schedule_once(self._show_loading, 1.4)
        # Step 5: Login pe jao
        Clock.schedule_once(self._go_to_login,  3.2)
 
    def _show_name(self, dt):
        Animation(opacity=1, duration=0.6).start(self.ids.app_name)
 
    def _show_tagline(self, dt):
        Animation(opacity=1, duration=0.6).start(self.ids.tagline)
 
    def _show_loading(self, dt):
        Animation(opacity=1, duration=0.4).start(self.ids.loading_bar)
        # Loading bar animate karo
        anim = Animation(value=100, duration=1.6)
        anim.start(self.ids.progress)
 
    def _go_to_login(self, dt):
        MDApp.get_running_app().switch_screen("login")