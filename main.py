from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.bottomsheet.bottomsheet import MDLabel
from kivymd.uix.segmentedbutton import MDSegmentedButtonItem
from kivymd.uix.segmentedbutton import MDSegmentedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import *
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText

import os

from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.utils import platform
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.lang.builder import Builder


if platform != 'android':
    Window.size = (480,800)


Builder.load_string('''
<HomeScreen>:
    canvas.before:
        Color:
            rgba: 0.9, 0.9, 0.9, 1  # Light gray background color
        Rectangle:
            pos: self.pos
            size: self.size    
    MDBoxLayout:
        orientation: 'vertical'
        pos_hint: {'center_y': .9}
        MDLabel:
            text: 'Pomodoable'
            halign: 'center'
    MDExtendedFabButton:
        size_hint_x: .1
        pos_hint: {'center_x': .25,'center_y': .8}
        fab_state: 'expand'
        on_press: root.setting_one()
        MDExtendedFabButtonText:
            text: '25'     
           
    MDExtendedFabButton:
        size_hint_x: .1
        pos_hint: {'center_x': .5,'center_y': .8}
        fab_state: 'expand'
        on_press: root.setting_two()
        MDExtendedFabButtonText:
            text: '50'     
    MDExtendedFabButton:
        size_hint_x: .1
        pos_hint: {'center_x': .75,'center_y': .8}
        fab_state: 'expand'
        on_release:
            root.show_custom_time_dialog()
        MDExtendedFabButtonText:
            text: 'C'
    MDBoxLayout:
        halign: 'center'
        MDLabel:
            id: time_display
            text: '00:00'
            halign: 'center'
            
''')

"""TO DO:
1. Fix the dialog box # DONE
2. display time # Displays current work time :)
3. countdown logic
4. fix ui
"""

class WindowManager(ScreenManager):
    pass

class HomeScreen(Screen):
    dialog = None
    work_time = 0
    short_break = 0
    long_break = 0
    mode = 1
    cycle = 0
    def setting_one(self):
        self.work_time = 25
        self.short_break = 5
        self.long_break = 10
        self.display_time()
        print(self.work_time,self.short_break,self.long_break)
    def setting_two(self):
        self.work_time = 50
        self.short_break = 10
        self.long_break = 15
        self.display_time()
        print(self.work_time,self.short_break,self.long_break)

    def show_custom_time_dialog(self):
        if not self.dialog:
            # Create the text field as a separate variable
            self.custom_work_time = MDTextField(
                MDTextFieldHintText(text='Work:'),
                input_filter='int',
                required=True
            )
            self.custom_break_time = MDTextField(
                MDTextFieldHintText(text='Short Break:'),
                input_filter='int',
                required=True
            )
            self.custom_long_break_time = MDTextField(
                MDTextFieldHintText(text='Long Break:'),
                input_filter='int',
                required=True
            )
            
            self.dialog = MDDialog(
                MDDialogHeadlineText(
                    text='Enter Custom Time'
                ),
                MDDialogContentContainer(
                    self.custom_work_time  # Use the reference here
                ),
                MDDialogContentContainer(
                    self.custom_break_time  # Use the reference here
                ),
                MDDialogContentContainer(
                    self.custom_long_break_time  # Use the reference here
                ),
                MDDialogButtonContainer(
                    MDButton(MDButtonText(text='Cancel'), style='text', on_release=self.close_dialog),
                    MDButton(MDButtonText(text='Enter'), style='tonal', on_release=self.set_custom_time)
                )
            )
            self.dialog.open()

    def close_dialog(self, obj):
        self.dialog.dismiss()
        self.dialog = None

    def set_custom_time(self, obj):
        custom_work_time = self.custom_work_time.text
        custom_short_break = self.custom_break_time.text
        custom_long_break = self.custom_long_break_time.text
        try:
            self.work_time = int(custom_work_time)
            self.short_break = int(custom_short_break)
            self.long_break = int(custom_long_break)
            self.dialog.dismiss()
            self.dialog = None
            self.display_time()
            print(self.work_time, self.short_break, self.long_break)
        except Exception as e:
            print(f'ERROR: {e}')

    def display_time(self):
        self.ids.time_display.text = str(self.work_time)

class Main(MDApp):
    def __init__(self, **kwargs):
        self.title = 'Pomodoable'
        super().__init__(**kwargs)
    
    def build(self):
        self.wm = WindowManager()
        screens = [
            HomeScreen(name='home')
        ]
        for screen in screens:
            self.wm.add_widget(screen)
        self.wm.current = 'home'
        return self.wm
    


if __name__ == '__main__':
    Main().run()