from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen, CardTransition
from kivy.uix.image import Image
from kivy.properties import StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.window import Window
from sqlite3 import connect
from os.path import join
from qrcode import make
from plyer import uniqueid, notification


class QRCode(ButtonBehavior, Image):
    def on_release(self):
        self.export_to_png('qr_code.png')
        notification.notify(message='QR code saved to Gallery', toast=True)


class EditScreen(Screen):
    """
    Screen to edit information about a bag
    """

    bag_id = StringProperty()
    bag_name = StringProperty()

    def save(self):
        """
        Save info of bag
        """

        # Ensure name is not blank
        if self.name_input.text:
            # Update database
            app.cursor.execute('''
            UPDATE bags SET
            name=?,
            description=?
            WHERE id=?
            ''', (self.name_input.text, self.description_input.text, int(self.bag_id),))
            app.connection.commit()


class BagsScreen(Screen):
    """
    Screen to show available bags
    """

    def new_bag(self):
        """
        Add new bag to screen
        """

        # Find id of current bag
        app.cursor.execute('SELECT MAX(id) FROM bags')

        if (row_id := app.cursor.fetchone()[0]) is None:
            row_id = 0
        row_id += 1
        row_id = str(row_id)

        # Create qr code
        qr = make(SEPARATOR.join([IDENTIFIER, uniqueid.get_uid(), row_id]))
        qr.save(join(app.user_data_dir, row_id + '.png'))

        # Update database
        app.cursor.execute('''
        INSERT INTO bags (rowid) VALUES (?)
        ''', (int(row_id),))
        app.connection.commit()

        app.cursor.execute('SELECT name FROM bags WHERE id=?', (row_id,))

        # Configure edit screen
        edit_screen = self.manager.get_screen('edit')
        edit_screen.bag_id = row_id
        edit_screen.bag_name = app.cursor.fetchone()[0]

        # Switch screen
        self.manager.transition = CardTransition(direction='left')
        self.manager.current = 'edit'


class PackerApp(MDApp):
    """
    App to be run
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.connection = connect(join(self.user_data_dir, 'packer.db'))
        self.cursor = self.connection.cursor()

        # Create tables
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS bags (
            id INTEGER PRIMARY KEY UNIQUE,
            name TEXT NOT NULL DEFAULT 'New Bag',
            description TEXT NOT NULL DEFAULT ''
        )
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            bag_id INTEGER,
            name TEXT NOT NULL DEFAULT '',
            amount INTEGER DEFAULT 1,
            FOREIGN KEY(bag_id) REFERENCES bags(rowid)
        )
        ''')

    def build(self):
        """
        Configure application
        """

        self.icon = 'icon.png'
        self.title = 'Packer'

        return ScreenManager()

    def on_stop(self):
        """
        Perform operation when application is closed
        """

        self.connection.close()


# Define constants

IDENTIFIER = 'packer'
SEPARATOR = ':'

# Resize window
Window.size = 275, 475

# Run app
app = PackerApp()
app.run()
