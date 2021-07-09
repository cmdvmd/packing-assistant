from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window


class PackingApp(App):
    def build(self):
        """
        Configure application
        """

        self.icon = 'icon.png'
        self.title = 'Packing Assistant'
        return ScreenManager()


Window.clearcolor = 0.98, 0.98, 0.98, 1
Window.size = 250, 450

# Run app
app = PackingApp()
app.run()
