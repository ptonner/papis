import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import papis.api

main_window_glade_file = os.path.join(
    os.path.dirname(__file__),
    "main.glade"
)


class Pick(Gtk.window):
    pass


class Gui(object):

    def __init__(self):
        self.args = None
        self.win = None

    def main(self, args):
        self.args = args
        self.tree = Gtk.Builder()
        self.tree.add_from_file(main_window_glade_file)
        self.window = self.tree.get_object("main_window")
        self.window.connect("delete-event", Gtk.main_quit)
        self.window.show_all()
        Gtk.main()
