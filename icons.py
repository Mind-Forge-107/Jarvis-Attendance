from kivy.lang import Builder
from kivy.properties import StringProperty
from kivymd.icon_definitions import md_icons
from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem

# Corrected KV String
Builder.load_string(
    '''
<IconItem>:
    orientation: "horizontal"
    spacing: "12dp"

    MDIcon:
        icon: root.icon
        size_hint: None, None
        size: "24dp", "24dp"
        pos_hint: {"center_y": .5}

    MDLabel:
        text: root.text
        valign: "middle"


<PreviousMDIcons>:
    md_bg_color: self.theme_cls.bg_dark  # Fixed the background color

    MDBoxLayout:
        orientation: 'vertical'
        spacing: dp(10)
        padding: dp(20)

        MDBoxLayout:
            adaptive_height: True

            MDIconButton:
                icon: 'magnify'
                pos_hint: {'center_y': .5}

            MDTextField:
                id: search_field
                hint_text: 'Search icon'
                on_text: root.set_list_md_icons(self.text, True)

        RecycleView:
            id: rv
            key_viewclass: 'viewclass'
            key_size: 'height'

            RecycleBoxLayout:
                padding: dp(10), dp(10), 0, dp(10)
                default_size: None, dp(48)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'
'''
)

class IconItem(OneLineListItem):
    icon = StringProperty()
    text = StringProperty()


class PreviousMDIcons(MDScreen):
    def set_list_md_icons(self, text="", search=False):
        '''Builds a list of icons for the screen MDIcons.'''
        self.ids.rv.data = []
        for name_icon in md_icons.keys():
            if search and text not in name_icon:
                continue
            self.ids.rv.data.append(
                {
                    "viewclass": "IconItem",
                    "icon": name_icon,
                    "text": name_icon,
                }
            )


class MainApp(MDApp):
    def build(self):
        self.screen = PreviousMDIcons()
        return self.screen

    def on_start(self):
        self.screen.set_list_md_icons()


MainApp().run()
