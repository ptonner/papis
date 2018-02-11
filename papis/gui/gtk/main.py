import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk


import re
import papis.utils
import papis.config
import papis.database


class ListElement(Gtk.Label):

    def __init__(self, document):
        Gtk.Label.__init__(self)
        self.document = document
        self.match_format = papis.utils.format_doc(
            papis.config.get('match-format'), document
        )
        self.set_markup(
            papis.utils.format_doc(
                papis.config.get('header-format', section='rofi-gui'),
                self.document
            )
        )
        self.set_yalign(0.0)
        self.set_xalign(0.0)
        self.set_line_wrap(10.0)
        self.set_properties('can-focus', True)
        self.set_properties('has-focus', True)
        self.set_properties('has-tooltip', True)
        self.set_properties('tooltip-text', 'asf')
        self.set_properties('focus-padding', 20)

    def get_document(self):
        return self.document

    def get_match_format(self):
        return self.match_format

class ElementList(Gtk.ListBox):

    def __init__(self):
        Gtk.ListBox.__init__(self)

    def get_selected_index(self):
        return self.get_selected_row().get_index()

    def get_selected_document(self):
        return self.get_selected_row().get_children()[0].get_document()


class Gui(Gtk.Window):
    def __init__(self, documents=[], header_filter=None):

        Gtk.Window.__init__(self)
        self.lines = 50
        self.list_elements = []

        self.db = papis.database.get()

        self.set_decorated(False)
        self.set_title('Papis gtk picker')

        self.connect("key-press-event", self.handle_key)

        self.entry = Gtk.Entry()
        self.connect("key-release-event", self.handle_entry_key)
        self.entry.set_icon_from_icon_name(
            Gtk.EntryIconPosition(0),
            'search'
        )
        self.entry.set_icon_tooltip_text(
            Gtk.EntryIconPosition(0),
            'Query input'
        )

        self.listbox = ElementList()

        print('Vbox added')
        vbox = Gtk.VBox()
        vbox.add(self.entry)
        s = Gtk.ScrolledWindow()
        s.set_min_content_height(
            self.get_screen().get_height() * self.lines / 100
        )
        s.set_max_content_height(
            self.get_screen().get_height() * self.lines / 100
        )
        s.add(self.listbox)

        def filtering(el):
            m = el.get_children()[0].get_match_format()
            return re.match(
                '.*'+re.sub('  *', '\s*', self.entry.get_text()),
                m,
                re.I
            )

        self.listbox.set_filter_func(filtering)
        vbox.add(s)


        self.add(vbox)
        self.show_all()
        self.move(0,0)
        self.resize(
            self.get_screen().get_width(),
            2
        )

        if documents:
            self.update_list(documents)

        Gtk.main()

    def get(self):
        return self.listbox.get_selected_document()

    def get_selected_document(self):
        return self.listbox.get_selected_document()

    def update_list(self, documents):
        print('Creating ListElements')
        self.list_elements = [
            ListElement(doc) for doc in documents
        ]
        for el in self.list_elements:
            self.listbox.add(el)
        self.show_all()

    def focus_filter_prompt(self):
        self.entry.set_icon_from_icon_name(
            Gtk.EntryIconPosition(0),
            'search'
        )
        self.entry.grab_focus()

    def focus_query_prompt(self):
        self.entry.set_icon_from_icon_name(
            Gtk.EntryIconPosition(0),
            'server'
        )
        self.entry.grab_focus()

    def handle_entry_key(self, w, el):
        print('entry')
        self.listbox.invalidate_filter()

    def handle_key(self, w, el):
        print(el.get_keycode())
        print(el.get_keyval())
        print(el.string)
        #enter
        if el.get_keycode()[1] == 36:
            doc = self.listbox.get_selected_document()
            papis.document.open_in_browser(doc)
        elif el.keyval== Gdk.keyval_from_name('c')\
            and el.state == Gdk.CONTROL_MASK:
            print('hello')
        elif el.keyval == Gdk.keyval_from_name('c'):
            print('just c')
        # Escape
        elif el.get_keycode()[1] == 9:
            print('focusing')
            self.focus_filter_prompt()
        #elif el.get_keyval()[1] == ord(' '):
        #    print('focusing')
            #self.focus_query_prompt()
        #elif el.get_keyval()[1] == ord('o'):
        #    print(self.listbox.get_selected_row().get_children())
        elif el.get_keyval()[1] == ord('q'):
            Gtk.main_quit()


def pick(options, header_filter=None, body_filter=None, match_filter=None):
    return Gui(options, header_filter).get()
