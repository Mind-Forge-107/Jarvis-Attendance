from kivymd.app import MDApp
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine
from kivymd.uix.list import OneLineIconListItem, IconLeftWidget
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.navigationdrawer import MDNavigationLayout, MDNavigationDrawer
from kivymd.uix.screen import Screen
from kivymd.uix.screenmanager import ScreenManager
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDIconButton, MDFloatingActionButton, MDFlatButton
from func_con import launch_student_details, launch_train_data, launch_student_identification
from kivymd.uix.textfield import MDTextField
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivymd.theming import ThemeManager
from kivy.properties import ListProperty
from kivymd.uix.dialog import MDDialog

class HomeScreen(Screen):
    pass

class DashboardScreen(Screen):
    pass

class ToolsScreen(Screen):
    pass

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()  # Store app reference
        root_layout = MDBoxLayout(orientation="vertical")
        
        toolbar = MDTopAppBar(
            title="Settings",
            md_bg_color=self.app.theme_cls.primary_color,  # Use theme color
            specific_text_color=(1, 1, 1, 1),
            left_action_items=[['menu', lambda x: self.parent.parent.ids.nav_drawer.set_state("open")]],
            right_action_items=[['theme-light-dark', lambda x: self.app.toggle_theme()]],
            size_hint_y=None,
            height="56dp"
        )
        root_layout.add_widget(toolbar)

        scroll_view = MDScrollView()
        content_layout = MDBoxLayout(
            orientation="vertical",
            padding=("20dp", "10dp"),
            spacing="10dp",
            adaptive_height=True
        )

        # Account Panel
        account_content = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height="48dp",  # Match typical height of OneLineIconListItem
            padding=0,
            spacing=0
        )
        account_content.add_widget(OneLineIconListItem(text="Profile", on_release=lambda x: print("Profile clicked")))
        account_panel = MDExpansionPanel(
            panel_cls=MDExpansionPanelOneLine(text="Account"),
            content=account_content
        )
        content_layout.add_widget(account_panel)

        # Preferences Panel
        preferences_content = MDBoxLayout(
            orientation="vertical",
            padding=(0, "48dp", 0, 0)  # Add top padding to avoid overlap
        )
        preferences_content.add_widget(MDLabel(text="Theme Style:", theme_text_color="Secondary", halign="left"))
        # Theme Options as a List with dynamic checkmark
        self.theme_items = {}
        themes = ["Light", "Dark", "Orange", "Green", "Purple", "Pink", "Yellow"]
        for theme in themes:
            item = OneLineIconListItem(
                text=theme,
                on_release=lambda x, t=theme: self.app.set_theme(t)
            )
            # Add an IconLeftWidget by default with an empty icon
            item.add_widget(IconLeftWidget(icon=""))
            self.theme_items[theme] = item
            preferences_content.add_widget(item)
        preferences_panel = MDExpansionPanel(
            panel_cls=MDExpansionPanelOneLine(text="Preferences"),
            content=preferences_content
        )
        content_layout.add_widget(preferences_panel)

        # Security & Privacy Panel
        security_content = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height="144dp",  # 48dp per item (3 items)
            padding=(0, "48dp", 0, 0),  # Add top padding to avoid overlap
            spacing=0
        )
        security_content.add_widget(OneLineIconListItem(text="Change Password", on_release=lambda x: self.app.show_password_dialog()))
        security_content.add_widget(OneLineIconListItem(text="Change Email", on_release=lambda x: self.app.show_email_dialog()))
        security_content.add_widget(OneLineIconListItem(text="Set New PIN", on_release=lambda x: self.app.show_pin_dialog()))
        security_panel = MDExpansionPanel(
            panel_cls=MDExpansionPanelOneLine(text="Security & Privacy"),
            content=security_content
        )
        content_layout.add_widget(security_panel)

        # About Panel
        about_content = MDBoxLayout(
            orientation="vertical",
            padding=(0, "48dp", 0, 0)  # Add top padding to avoid overlap
        )
        about_content.add_widget(MDLabel(text="Jarvis v1.0.0"))
        about_content.add_widget(MDLabel(text="Intelligent Monitoring System"))
        about_content.add_widget(MDLabel(text="Release Date: 30-01-2025"))
        about_panel = MDExpansionPanel(
            panel_cls=MDExpansionPanelOneLine(text="About"),
            content=about_content
        )
        content_layout.add_widget(about_panel)

        scroll_view.add_widget(content_layout)
        root_layout.add_widget(scroll_view)
        self.add_widget(root_layout)

    def update_theme_ui(self, theme):
        # Update checkmark state for all items
        for item in self.theme_items.values():
            # Find the IconLeftWidget and update its icon
            for child in item.children:
                if isinstance(child, IconLeftWidget):
                    child.icon = "check" if item.text == theme else ""

class App_uiApp(MDApp):
    current_bg_color = ListProperty([0.95, 0.95, 0.95, 1])  # Default to Light background

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls = ThemeManager()
        self.theme_cls.theme_style = "Light"  # Default theme
        self.current_theme = "Light"  # Track the current theme
        # Custom background colors for each theme
        self.custom_bg_colors = {
            "Light": [0.95, 0.95, 0.95, 1],  # Light gray
            "Dark": [0.2, 0.2, 0.2, 1],      # Slightly lighter dark gray for better contrast
            "Orange": [1, 0.9, 0.8, 1],      # Light orange
            "Green": [0.8, 1, 0.8, 1],       # Light green
            "Purple": [0.9, 0.8, 1, 1],      # Light purple
            "Pink": [1, 0.8, 0.9, 1],        # Light pink
            "Yellow": [1, 1, 0.8, 1],        # Light yellow
        }
        # Set initial background color
        self.current_bg_color = self.custom_bg_colors[self.current_theme]

    def build(self):
        kv = Builder.load_string("""
#:import MDBoxLayout kivymd.uix.boxlayout.MDBoxLayout
#:import MDTopAppBar kivymd.uix.toolbar.MDTopAppBar
#:import MDLabel kivymd.uix.label.MDLabel
#:import MDNavigationDrawer kivymd.uix.navigationdrawer.MDNavigationDrawer
#:import ScreenManager kivymd.uix.screenmanager.ScreenManager
#:import MDList kivymd.uix.list.MDList
#:import OneLineIconListItem kivymd.uix.list.OneLineIconListItem
#:import IconLeftWidget kivymd.uix.list.IconLeftWidget
#:import MDCard kivymd.uix.card.MDCard
#:import MDIconButton kivymd.uix.button.MDIconButton
#:import MDFloatingActionButton kivymd.uix.button.MDFloatingActionButton
#:import MDTextField kivymd.uix.textfield.MDTextField
#:import MDGridLayout kivymd.uix.gridlayout.MDGridLayout
#:import ScrollView kivy.uix.scrollview.ScrollView

MDNavigationLayout:
    ScreenManager:
        id: screen_manager
        HomeScreen:
            name: "home"
            canvas.before:
                Color:
                    rgba: app.current_bg_color  # Use dynamic background color
                Rectangle:
                    pos: self.pos
                    size: self.size
            MDBoxLayout:
                orientation: "vertical"
                MDTopAppBar:
                    title: "Home"
                    md_bg_color: app.theme_cls.primary_color  # Use theme color
                    specific_text_color: 1, 1, 1, 1
                    left_action_items: [['menu', lambda x: app.root.ids.nav_drawer.set_state("open")]]
                    right_action_items: [['theme-light-dark', lambda x: app.toggle_theme()]]
                    size_hint_y: None
                    height: "56dp"
                
                MDBoxLayout:
                    orientation: "vertical"
                    padding: "20dp"
                    spacing: "10dp"
                    
                    MDBoxLayout:
                        orientation: "horizontal"
                        size_hint_y: None
                        height: "50dp"
                        
                        MDLabel:
                            text: "welcome to jarvis !"
                            font_style: "H5"
                            halign: "left"
                            bold: True
                            padding: "0dp", "10dp"
                            theme_text_color: "Primary"  # Use theme color
                        
                        MDIconButton:
                            icon: "bell-outline"
                            theme_text_color: "Primary"  # Use theme color
                            pos_hint: {"center_y": 0.5}
                            on_release: print("Notification button pressed")
                    
                    MDBoxLayout:
                        size_hint_y: None
                        height: "120dp"
                        spacing: "10dp"
                        
                        MDCard:
                            size_hint_x: 0.7
                            orientation: "vertical"
                            padding: "10dp"
                            radius: [20, 20, 20, 20]
                            md_bg_color: app.theme_cls.bg_light if app.theme_cls.theme_style == "Light" else app.theme_cls.bg_dark
                            
                            MDLabel:
                                text: "Let's Get started with:"
                                halign: "left"
                                theme_text_color: "Secondary"
                                size_hint_y: None
                                height: "30dp"
                            
                            MDBoxLayout:
                                orientation: "horizontal"
                                spacing: "10dp"
                                padding: "5dp", 0, 0, 0  # Move icons slightly to the left
                                
                                # Icon-Text Pair 1: Detection
                                MDBoxLayout:
                                    orientation: "vertical"
                                    MDIconButton:
                                        icon: "camera"
                                        theme_text_color: "Custom"
                                        text_color: 1, 0, 0, 1  # Red color for camera icon
                                        halign: "center"
                                        on_release: print("Detection button pressed")
                                    MDLabel:
                                        text: "detection"
                                        theme_text_color: "Primary"  # Use theme color
                                        halign: "left"
                                        size_hint_y: None
                                        height: "20dp"
                                        
                                
                                # Icon-Text Pair 2: Training
                                MDBoxLayout:
                                    orientation: "vertical"
                                    MDIconButton:
                                        icon: "database"
                                        theme_text_color: "Custom"
                                        text_color: 1, 0.5, 0, 1  # Orange color for database icon
                                        halign: "center"
                                        on_release: print("Training button pressed")
                                    MDLabel:
                                        text: "training"
                                        theme_text_color: "Primary"  # Use theme color
                                        halign: "left"
                                        size_hint_y: None
                                        height: "20dp"
                                
                                # Icon-Text Pair 3: Jarvis AI
                                MDBoxLayout:
                                    orientation: "vertical"
                                    MDIconButton:
                                        icon: "auto-fix"
                                        theme_text_color: "Primary"  # Use theme color
                                        halign: "center"
                                        on_release: print("Jarvis AI button pressed")
                                    MDLabel:
                                        text: "Jarvis AI"
                                        theme_text_color: "Primary"  # Use theme color
                                        halign: "left"
                                        size_hint_y: None
                                        height: "20dp"
                                
                                # Icon-Text Pair 4: More Tools
                                MDBoxLayout:
                                    orientation: "vertical"
                                    MDIconButton:
                                        icon: "chevron-right"
                                        theme_text_color: "Primary"  # Use theme color
                                        halign: "center"
                                        on_release:
                                            screen_manager.current = "tools"
                                            app.root.ids.nav_drawer.set_state("close")
                                        
                                    MDLabel:
                                        text: "more tools"
                                        theme_text_color: "Primary"  # Use theme color
                                        halign: "left"
                                        size_hint_y: None
                                        height: "20dp"
                        
                        MDCard:
                            size_hint_x: 0.3
                            radius: [20, 20, 20, 20]
                            md_bg_color: app.theme_cls.bg_light if app.theme_cls.theme_style == "Light" else app.theme_cls.bg_dark
                            MDBoxLayout:
                                orientation: "vertical"
                                MDIconButton:
                                    icon: "account-circle-outline"
                                    icon_size: "96dp"
                                    theme_text_color: "Primary"  # Use theme color
                                    halign: "center"
                                    on_release: print("Account button pressed")
                    
                    MDBoxLayout:
                        orientation: "horizontal"
                        padding: "10dp", "10dp"
                        
                        MDTextField:
                            id: search_field
                            hint_text: "Search"
                            mode: "round"
                            size_hint_x: 0.8
                        MDIconButton:
                            icon: "sort-variant"
                            theme_text_color: "Primary"  # Use theme color
                            size_hint_x: 0.1
                        MDIconButton:
                            icon: "view-grid-outline"
                            theme_text_color: "Primary"  # Use theme color
                            size_hint_x: 0.1
                    
                    MDLabel:
                        text: "No recent data available"
                        halign: "center"
                        theme_text_color: "Secondary"
                        size_hint_y: None
                        height: "50dp"

        DashboardScreen:
            name: "dashboard"
            canvas.before:
                Color:
                    rgba: app.current_bg_color  # Use dynamic background color
                Rectangle:
                    pos: self.pos
                    size: self.size
            MDBoxLayout:
                orientation: "vertical"
                MDTopAppBar:
                    title: "Dashboard"
                    md_bg_color: app.theme_cls.primary_color  # Use theme color
                    specific_text_color: 1, 1, 1, 1
                    left_action_items: [['menu', lambda x: app.root.ids.nav_drawer.set_state("open")]]
                    right_action_items: [['theme-light-dark', lambda x: app.toggle_theme()]]
                    size_hint_y: None
                    height: "56dp"
                MDLabel:
                    text: "Dashboard Screen"
                    halign: "center"
                    theme_text_color: "Primary"  # Use theme color

        ToolsScreen:
            name: "tools"
            canvas.before:
                Color:
                    rgba: app.current_bg_color  # Use dynamic background color
                Rectangle:
                    pos: self.pos
                    size: self.size
            MDBoxLayout:
                orientation: "vertical"
                MDTopAppBar:
                    title: "Tools"
                    md_bg_color: app.theme_cls.primary_color  # Use theme color
                    specific_text_color: 1, 1, 1, 1
                    left_action_items: [['menu', lambda x: app.root.ids.nav_drawer.set_state("open")]]
                    right_action_items: [['theme-light-dark', lambda x: app.toggle_theme()]]
                    size_hint_y: None
                    height: "56dp"
                
                # Main content with ScrollView
                ScrollView:
                    do_scroll_x: False
                    do_scroll_y: True
                    MDBoxLayout:
                        orientation: "vertical"
                        padding: "20dp"
                        spacing: "20dp"
                        size_hint_y: None
                        height: self.minimum_height
                        
                        MDGridLayout:
                            cols: 4
                            spacing: "20dp"
                            padding: "10dp"
                            size_hint_y: None
                            height: self.minimum_height
                            
                            # Button 1: Student Details
                            MDBoxLayout:
                                orientation: "vertical"
                                size_hint_y: None
                                height: "150dp"
                                MDCard:
                                    size_hint: None, None
                                    size: "80dp", "80dp"
                                    radius: [15, 15, 15, 15]
                                    md_bg_color: app.theme_cls.bg_light if app.theme_cls.theme_style == "Light" else app.theme_cls.bg_dark
                                    pos_hint: {"center_x": 0.5}
                                    MDIconButton:
                                        icon: "face-man-profile"
                                        theme_text_color: "Primary"  # Use theme color
                                        pos_hint: {"center_x": 0.5, "center_y": 0.5}
                                        icon_size: "40dp"
                                        on_release:
                                            print("Student Details button pressed")
                                MDLabel:
                                    text: "Student Details"
                                    halign: "center"
                                    theme_text_color: "Secondary"
                                    size_hint_y: None
                                    height: "30dp"
                            
                            # Button 2: Attendance Marking
                            MDBoxLayout:
                                orientation: "vertical"
                                size_hint_y: None
                                height: "150dp"
                                MDCard:
                                    size_hint: None, None
                                    size: "80dp", "80dp"
                                    radius: [15, 15, 15, 15]
                                    md_bg_color: app.theme_cls.bg_light if app.theme_cls.theme_style == "Light" else app.theme_cls.bg_dark
                                    pos_hint: {"center_x": 0.5}
                                    MDIconButton:
                                        icon: "image-filter-center-focus"
                                        theme_text_color: "Primary"  # Use theme color
                                        pos_hint: {"center_x": 0.5, "center_y": 0.5}
                                        icon_size: "40dp"
                                        on_release:
                                            print("Attendance Marking button pressed")
                                MDLabel:
                                    text: "Student Identification"
                                    halign: "center"
                                    theme_text_color: "Secondary"
                                    size_hint_y: None
                                    height: "30dp"
                            
                            # Button 3: Jarvis AI
                            MDBoxLayout:
                                orientation: "vertical"
                                size_hint_y: None
                                height: "150dp"
                                MDCard:
                                    size_hint: None, None
                                    size: "80dp", "80dp"
                                    radius: [15, 15, 15, 15]
                                    md_bg_color: app.theme_cls.bg_light if app.theme_cls.theme_style == "Light" else app.theme_cls.bg_dark
                                    pos_hint: {"center_x": 0.5}
                                    MDIconButton:
                                        icon: "auto-fix"
                                        theme_text_color: "Primary"  # Use theme color
                                        pos_hint: {"center_x": 0.5, "center_y": 0.5}
                                        icon_size: "40dp"
                                        on_release:
                                            print("Jarvis AI button pressed")
                                MDLabel:
                                    text: "Jarvis AI"
                                    halign: "center"
                                    theme_text_color: "Secondary"
                                    size_hint_y: None
                                    height: "30dp"
                            
                            # Button 4: Train Data
                            MDBoxLayout:
                                orientation: "vertical"
                                size_hint_y: None
                                height: "150dp"
                                MDCard:
                                    size_hint: None, None
                                    size: "80dp", "80dp"
                                    radius: [15, 15, 15, 15]
                                    md_bg_color: app.theme_cls.bg_light if app.theme_cls.theme_style == "Light" else app.theme_cls.bg_dark
                                    pos_hint: {"center_x": 0.5}
                                    MDIconButton:
                                        icon: "database"
                                        theme_text_color: "Primary"  # Use theme color
                                        pos_hint: {"center_x": 0.5, "center_y": 0.5}
                                        icon_size: "40dp"
                                        on_release:
                                            print("Train Data button pressed")
                                MDLabel:
                                    text: "Train Data"
                                    halign: "center"
                                    theme_text_color: "Secondary"
                                    size_hint_y: None
                                    height: "30dp"
                            
                            # Button 5: Live Class Recording (New Row)
                            MDBoxLayout:
                                orientation: "vertical"
                                size_hint_y: None
                                height: "150dp"
                                MDCard:
                                    size_hint: None, None
                                    size: "80dp", "80dp"
                                    radius: [15, 15, 15, 15]
                                    md_bg_color: app.theme_cls.bg_light if app.theme_cls.theme_style == "Light" else app.theme_cls.bg_dark
                                    pos_hint: {"center_x": 0.5}
                                    MDIconButton:
                                        icon: "video"
                                        theme_text_color: "Primary"  # Use theme color
                                        pos_hint: {"center_x": 0.5, "center_y": 0.5}
                                        icon_size: "40dp"
                                        on_release:
                                            print("Live Class Recording button pressed")
                                MDLabel:
                                    text: "Live Class Recording"
                                    halign: "center"
                                    theme_text_color: "Secondary"
                                    size_hint_y: None
                                    height: "30dp"
                            
                            # Button 6: Activity Monitoring (New Row)
                            MDBoxLayout:
                                orientation: "vertical"
                                size_hint_y: None
                                height: "150dp"
                                MDCard:
                                    size_hint: None, None
                                    size: "80dp", "80dp"
                                    radius: [15, 15, 15, 15]
                                    md_bg_color: app.theme_cls.bg_light if app.theme_cls.theme_style == "Light" else app.theme_cls.bg_dark
                                    pos_hint: {"center_x": 0.5}
                                    MDIconButton:
                                        icon: "electron-framework"
                                        theme_text_color: "Primary"  # Use theme color
                                        pos_hint: {"center_x": 0.5, "center_y": 0.5}
                                        icon_size: "40dp"
                                        on_release:
                                            print("Activity Monitoring button pressed")
                                MDLabel:
                                    text: "Activity Monitoring"
                                    halign: "center"
                                    theme_text_color: "Secondary"
                                    size_hint_y: None
                                    height: "30dp"
                            
                            # Button 7: Dress Code Monitoring (New Row)
                            MDBoxLayout:
                                orientation: "vertical"
                                size_hint_y: None
                                height: "150dp"
                                MDCard:
                                    size_hint: None, None
                                    size: "80dp", "80dp"
                                    radius: [15, 15, 15, 15]
                                    md_bg_color: app.theme_cls.bg_light if app.theme_cls.theme_style == "Light" else app.theme_cls.bg_dark
                                    pos_hint: {"center_x": 0.5}
                                    MDIconButton:
                                        icon: "tshirt-crew"
                                        theme_text_color: "Primary"  # Use theme color
                                        pos_hint: {"center_x": 0.5, "center_y": 0.5}
                                        icon_size: "40dp"
                                        on_release:
                                            print("Dress Code Monitoring button pressed")
                                MDLabel:
                                    text: "Dress Code Monitoring"
                                    halign: "center"
                                    theme_text_color: "Secondary"
                                    size_hint_y: None
                                    height: "30dp"
                            
                                 

                            # Button 8: Report Generation (New Row)
                            MDBoxLayout:
                                orientation: "vertical"
                                size_hint_y: None
                                height: "150dp"
                                MDCard:
                                    size_hint: None, None
                                    size: "80dp", "80dp"
                                    radius: [15, 15, 15, 15]
                                    md_bg_color: app.theme_cls.bg_light if app.theme_cls.theme_style == "Light" else app.theme_cls.bg_dark
                                    pos_hint: {"center_x": 0.5}
                                    MDIconButton:
                                        icon: "clipboard-check-multiple-outline"
                                        theme_text_color: "Primary"  # Use theme color
                                        pos_hint: {"center_x": 0.5, "center_y": 0.5}
                                        icon_size: "40dp"
                                        on_release:
                                            print("Report Generation button pressed")
                                MDLabel:
                                    text: "Report Generation"
                                    halign: "center"
                                    theme_text_color: "Secondary"
                                    size_hint_y: None
                                    height: "30dp"




                            # Button 9: Event Scheduling (New Row)
                            MDBoxLayout:
                                orientation: "vertical"
                                size_hint_y: None
                                height: "150dp"
                                MDCard:
                                    size_hint: None, None
                                    size: "80dp", "80dp"
                                    radius: [15, 15, 15, 15]
                                    md_bg_color: app.theme_cls.bg_light if app.theme_cls.theme_style == "Light" else app.theme_cls.bg_dark
                                    pos_hint: {"center_x": 0.5}
                                    MDIconButton:
                                        icon: "calendar-clock-outline"
                                        theme_text_color: "Primary"  # Use theme color
                                        pos_hint: {"center_x": 0.5, "center_y": 0.5}
                                        icon_size: "40dp"
                                        on_release:
                                            print("Event Scheduling button pressed")
                                MDLabel:
                                    text: "Event Scheduling"
                                    halign: "center"
                                    theme_text_color: "Secondary"
                                    size_hint_y: None
                                    height: "30dp"
                   

                            # Button 10: Attendance Tracking (New Row)
                            MDBoxLayout:
                                orientation: "vertical"
                                size_hint_y: None
                                height: "150dp"
                                MDCard:
                                    size_hint: None, None
                                    size: "80dp", "80dp"
                                    radius: [15, 15, 15, 15]
                                    md_bg_color: app.theme_cls.bg_light if app.theme_cls.theme_style == "Light" else app.theme_cls.bg_dark
                                    pos_hint: {"center_x": 0.5}
                                    MDIconButton:
                                        icon: "all-inclusive"
                                        theme_text_color: "Primary"  # Use theme color
                                        pos_hint: {"center_x": 0.5, "center_y": 0.5}
                                        icon_size: "40dp"
                                        on_release:
                                            print("Event Scheduling button pressed")
                                MDLabel:
                                    text: "Attendance Tracking"
                                    halign: "center"
                                    theme_text_color: "Secondary"
                                    size_hint_y: None
                                    height: "30dp"


                                
                            # Button 11: Sentiment Tracking (New Row)
                            MDBoxLayout:
                                orientation: "vertical"
                                size_hint_y: None
                                height: "150dp"
                                MDCard:
                                    size_hint: None, None
                                    size: "80dp", "80dp"
                                    radius: [15, 15, 15, 15]
                                    md_bg_color: app.theme_cls.bg_light if app.theme_cls.theme_style == "Light" else app.theme_cls.bg_dark
                                    pos_hint: {"center_x": 0.5}
                                    MDIconButton:
                                        icon: "emoticon-excited-outline"
                                        theme_text_color: "Primary"  # Use theme color
                                        pos_hint: {"center_x": 0.5, "center_y": 0.5}
                                        icon_size: "40dp"
                                        on_release:
                                            print("Sentiment Tracking button pressed")
                                MDLabel:
                                    text: "Sentiment Tracking"
                                    halign: "center"
                                    theme_text_color: "Secondary"
                                    size_hint_y: None
                                    height: "30dp"



                                 

        SettingsScreen:
            name: "settings"
            canvas.before:
                Color:
                    rgba: app.current_bg_color  # Use dynamic background color
                Rectangle:
                    pos: self.pos
                    size: self.size

    MDNavigationDrawer:
        id: nav_drawer
        md_bg_color: app.theme_cls.primary_color  # Use theme color
        BoxLayout:
            orientation: "vertical"
            spacing: "8dp"
            padding: "8dp"
            MDList:
                OneLineIconListItem:
                    text: "Home"
                    on_release:
                        screen_manager.current = "home"
                        app.root.ids.nav_drawer.set_state("close")
                    IconLeftWidget:
                        icon: "home"
                OneLineIconListItem:
                    text: "Dashboard"
                    on_release:
                        screen_manager.current = "dashboard"
                        app.root.ids.nav_drawer.set_state("close")
                    IconLeftWidget:
                        icon: "view-dashboard"
                OneLineIconListItem:
                    text: "Tools"
                    on_release:
                        screen_manager.current = "tools"
                        app.root.ids.nav_drawer.set_state("close")
                    IconLeftWidget:
                        icon: "wrench"
                OneLineIconListItem:
                    text: "Settings"
                    on_release:
                        screen_manager.current = "settings"
                        app.root.ids.nav_drawer.set_state("close")
                    IconLeftWidget:
                        icon: "cog"
        """)
        return kv

    def on_start(self):
        self.root.ids.screen_manager.current = "home"
        self.root.ids.nav_drawer.set_state("close")
        # Update theme UI on start
        settings_screen = self.root.ids.screen_manager.get_screen("settings")
        settings_screen.update_theme_ui(self.current_theme)

    def toggle_theme(self):
        # Toggle only between Light and Dark
        current_theme = self.theme_cls.theme_style
        new_theme = "Dark" if current_theme == "Light" else "Light"
        self.set_theme(new_theme)

    def set_theme(self, theme):
        self.current_theme = theme
        # Update the background color
        self.current_bg_color = self.custom_bg_colors[theme]
        
        # Set the theme style and primary palette
        if theme in ["Light", "Dark"]:
            self.theme_cls.theme_style = theme
            self.theme_cls.primary_palette = "Blue"
        else:
            self.theme_cls.theme_style = "Light"  # Base theme for custom colors
            if theme == "Orange":
                self.theme_cls.primary_palette = "Orange"
            elif theme == "Green":
                self.theme_cls.primary_palette = "Green"
            elif theme == "Purple":
                self.theme_cls.primary_palette = "Purple"
            elif theme == "Pink":
                self.theme_cls.primary_palette = "Pink"
            elif theme == "Yellow":
                self.theme_cls.primary_palette = "Yellow"
        
        print(f"Theme set to {theme}")
        # Update the UI in SettingsScreen
        settings_screen = self.root.ids.screen_manager.get_screen("settings")
        if settings_screen:
            settings_screen.update_theme_ui(theme)

    def show_theme_picker(self):
        print("Theme picker clicked")

    def show_password_dialog(self):
        print("Change Password clicked")

    def show_email_dialog(self):
        print("Change Email clicked")

    def show_pin_dialog(self):
        print("Set New PIN clicked")


if __name__ == "__main__":
    App_uiApp().run()