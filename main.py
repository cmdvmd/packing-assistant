from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import StringProperty
from kivy.core.window import Window


class Bag(ButtonBehavior, BoxLayout):
    """
    Widget to represent a bag on `BagsScreen`
    """

    qr = StringProperty(' ')
    name = StringProperty(' ')
    description = StringProperty(' ')


class BagsScreen(Screen):
    """
    Screen to show available bags
    """

    def new_bag(self):
        """
        Add new bag to screen
        """


class PackerApp(MDApp):
    """
    App to be run
    """

    def build(self):
        """
        Configure application
        """

        self.icon = 'icon.png'
        self.title = 'Packer'

        return ScreenManager()


# Resize window
Window.size = 275, 475

# Run app
app = PackerApp()
app.run()
