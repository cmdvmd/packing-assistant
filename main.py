from kivymd.app import MDApp
from kivymd.uix.card import MDCardSwipe, MDCard
from kivy.uix.screenmanager import ScreenManager, Screen, CardTransition, NoTransition
from kivy.uix.image import Image
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.core.window import Window
from sqlite3 import connect
from os.path import join
from os import remove
from qrcode import make
from plyer import uniqueid, notification
from time import time
from re import match


class QRCode(ButtonBehavior, Image):
    """
    Clickable image showing a QR code
    """

    def on_release(self):
        """
        Save qr code to Gallery after being released
        """

        # Save file as time in milliseconds
        self.export_to_png(str(int(time())) + '.png')
        notification.notify(message='QR code saved to Gallery', toast=True)


class Bag(MDCardSwipe):
    """
    Clickable card showing information about a bag
    """

    id = NumericProperty()
    name = StringProperty()
    description = StringProperty()

    def items(self):
        """
        Switch screen to Items Screen
        """

        # Configure Items Screen
        items_screen = app.root.get_screen('items')
        items_screen.bag_id = self.id
        items_screen.bag_name = self.name
        items_screen.bag_description = self.description

        # Switch screen
        app.root.transition = CardTransition(direction='left')
        app.root.current = 'items'


class Item(MDCard):
    """
    Card showing information about an item in a bag
    """

    bag_id = NumericProperty()
    name = StringProperty()
    amount = NumericProperty()

    def update(self, focus):
        """
        Update amount of item in bag
        """

        new_amount = self.amount_field.text.strip()

        # Ensure entered amount is valid
        if not focus and match(r'^-?[0-9]+$', new_amount):
            # Update database
            app.cursor.execute('UPDATE items SET amount=? WHERE bag_id=? AND name=?', (int(new_amount), self.bag_id, self.name,))
            app.connection.commit()

            app.root.get_screen('items').add_items()
        # If not, reset text to previously stored value
        else:
            app.cursor.execute('SELECT amount FROM items WHERE bag_id=? AND name=?', (self.bag_id, self.name,))
            self.amount_field.text = str(app.cursor.fetchone()[0])


class ScanScreen(Screen):
    @staticmethod
    def back():
        """
        Switch screens to Bags Screen
        """

        app.root.transition = CardTransition(direction='right')
        app.root.current = 'bags'

    def on_enter(self, *args):
        """
        Get a list of all valid ids
        """

        app.cursor.execute('SELECT id FROM bags')
        self.bag_ids = list(map(lambda bag_id: str(bag_id[0]), app.cursor.fetchall()))

    def validate(self, symbols):
        for qr_code in symbols:
            try:
                # Ensure QR code is valid
                data = qr_code.data.decode().split(SEPARATOR)
                assert data[0] == IDENTIFIER
                assert data[1] == uniqueid.get_uid()
                assert data[2] in self.bag_ids

                # If valid, configure items screen
                app.cursor.execute('SELECT name, description FROM bags WHERE id=?', (int(data[2]),))

                items_screen = app.root.get_screen('items')
                items_screen.bag_id = int(data[2])
                items_screen.bag_name, items_screen.bag_description = app.cursor.fetchone()

                # Switch screen
                app.root.transition = CardTransition(direction='left')
                app.root.current = 'items'

            except (AssertionError, IndexError) as e:
                # If invalid, notify user
                notification.notify(message='Invalid QR code', toast=True)


class EditScreen(Screen):
    """
    Screen to edit information about a bag
    """

    bag_id = NumericProperty()
    bag_name = StringProperty()
    bag_description = StringProperty()

    def save(self):
        """
        Save info of bag
        """

        # Ensure name is not blank
        if self.name_input.text.strip():
            # Update database
            app.cursor.execute('''
            UPDATE bags SET
            name=?,
            description=?
            WHERE id=?
            ''', (self.name_input.text, self.description_input.text, self.bag_id,))
            app.connection.commit()

            # Configure items screen
            items_screen = self.manager.get_screen('items')
            items_screen.bag_id = self.bag_id
            items_screen.bag_name = self.name_input.text
            items_screen.bag_description = self.description_input.text

            # Switch screen
            self.manager.transition = NoTransition()
            self.manager.current = 'items'


class ItemsScreen(Screen):
    """
    Screen to view and edit items in a bag
    """

    bag_id = NumericProperty()
    bag_name = StringProperty()
    bag_description = StringProperty()

    def on_enter(self, *args):
        """
        Schedule an event to add items to screen
        """

        Clock.schedule_once(lambda dt: self.add_items(), 0)

    def on_pre_leave(self, *args):
        """
        Delete removed items
        """

        app.cursor.execute('DELETE FROM items WHERE amount<=0')
        app.connection.commit()

    def back(self):
        """
        Switch screen to Bags Screen
        """

        self.manager.transition = CardTransition(direction='right')
        self.manager.current = 'bags'

    def edit(self):
        """
        Switch screen to Edit Screen
        """

        # Configure edit screen
        edit_screen = self.manager.get_screen('edit')
        edit_screen.bag_id = self.bag_id
        edit_screen.bag_name = self.bag_name
        edit_screen.bag_description = self.bag_description

        # Switch screen
        self.manager.transition = NoTransition()
        self.manager.current = 'edit'

    def add_items(self):
        """
        Add items to list on screen
        """

        # Clear current list
        self.item_list.clear_widgets()

        # Get all items in bag
        app.cursor.execute('SELECT name, amount FROM items WHERE bag_id=?', (self.bag_id,))
        items = app.cursor.fetchall()
        items.sort(key=lambda found: found[0].lower())

        # Add items to screen
        for item in items:
            self.item_list.add_widget(Item(
                bag_id=self.bag_id,
                name=item[0],
                amount=item[1]
            ))

    def new_item(self):
        """
        Add an item to a bag
        """

        # Get item
        item = self.item_field.text

        # Ensure item field is not empty
        if item:
            # Check if item already exists
            app.cursor.execute('SELECT name FROM items WHERE bag_id=? AND UPPER(name)=?', (self.bag_id, item.upper(),))
            if stored_name := app.cursor.fetchone():
                app.increment(stored_name[0], 1)
            # If not, add to database
            else:
                app.cursor.execute('INSERT INTO items (bag_id, name) VALUES (?, ?)', (self.bag_id, item,))
                app.connection.commit()
                self.add_items()

            # Reset item field text
            self.item_field.text = ''


class BagsScreen(Screen):
    """
    Screen to show available bags
    """

    def on_enter(self, *args):
        """
        Schedule an event to add bags to screen
        """

        Clock.schedule_once(lambda dt: self.add_bags(), 0)

    def add_bags(self):
        """
        Add bags to list on screen
        """

        # Clear current list
        self.bag_list.clear_widgets()

        # Get all bags
        app.cursor.execute('SELECT id, name, description FROM bags')
        for bag in app.cursor.fetchall():
            # Add a new bag to the screen
            self.bag_list.add_widget(Bag(
                id=bag[0],
                name=bag[1],
                description=bag[2]
            ))

    def new_bag(self):
        """
        Add new bag to screen
        """

        # Find id of current bag
        app.cursor.execute('SELECT MAX(id) FROM bags')

        if (row_id := app.cursor.fetchone()[0]) is None:
            row_id = 0
        row_id += 1

        # Create qr code
        qr = make(SEPARATOR.join([IDENTIFIER, uniqueid.get_uid(), str(row_id)]))
        qr.save(join(app.user_data_dir, str(row_id) + '.png'))

        # Update database
        app.cursor.execute('INSERT INTO bags (rowid) VALUES (?)', (row_id,))
        app.connection.commit()

        # Configure edit screen
        edit_screen = self.manager.get_screen('edit')
        edit_screen.bag_id = row_id
        edit_screen.bag_name, edit_screen.bag_description = get_data(row_id)

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
            name TEXT NOT NULL,
            amount INTEGER DEFAULT 1,
            FOREIGN KEY(bag_id) REFERENCES bags(rowid)
        )
        ''')

    def delete(self, bag):
        """
        Remove bag from database

        :param bag: Bag to be removed
        """

        # Delete from database
        self.cursor.execute('DELETE FROM bags WHERE id=?', (bag.id,))
        app.connection.commit()

        # Delete QR code
        remove(join(self.user_data_dir, str(bag.id) + '.png'))

        # Update bags screen
        self.root.get_screen('bags').add_bags()

    def increment(self, item, amount):
        items_screen = self.root.get_screen('items')

        app.cursor.execute('UPDATE items SET amount = amount + ? WHERE bag_id=? AND name=?', (amount, items_screen.bag_id, item,))
        app.connection.commit()

        # Update items screen
        items_screen.add_items()

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


def get_data(row_id):
    """
    Get name and description of a bag by ID

    :param row_id: ID of bag in database
    :return: Name and description of bag
    """

    app.cursor.execute('SELECT name, description FROM bags WHERE id=?', (row_id,))
    return app.cursor.fetchone()


# Define constants

IDENTIFIER = 'packer'
SEPARATOR = ':'

# Resize window
Window.size = 275, 475

# Run app
app = PackerApp()
app.run()
