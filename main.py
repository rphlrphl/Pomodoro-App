from kivy.uix.accordion import ListProperty
from kivy.uix.accordion import NumericProperty
from kivymd.uix.bottomsheet.bottomsheet import MDIconButton
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.bottomsheet.bottomsheet import MDLabel
from kivymd.uix.segmentedbutton import MDSegmentedButtonItem
from kivymd.uix.segmentedbutton import MDSegmentedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import *
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText

import os
import time
import datetime

from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.utils import platform
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.lang.builder import Builder
from kivy.properties import NumericProperty, ListProperty
from kivy.clock import Clock
from kivy.core.audio import SoundLoader


if platform != 'android':
    Window.size = (480,800)


Builder.load_string('''
<HomeScreen>:
    canvas.before:
        Color:
            id: background
            rgba: root.test  # Light gray background color
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
                    
    MDBoxLayout:
        orientation: 'horizontal'
        spacing: '10dp'
        padding: '10dp'
        size_hint: None, None
        size: self.minimum_size
        pos_hint: {'center_x': 0.5, 'center_y': 0.3}
        MDIconButton:
            id: start_button
            icon: 'play'
            style: "tonal"
            theme_font_size: "Custom"
            font_size: "48sp"
            radius: [self.height / 2, ]
            size_hint: None, None
            size: "60dp", "60dp"
            pos_hint: {'center_x': .9,'center_y': .3}
            on_press: root.start_timer()
            disabled: root.current_time == 0        
        MDIconButton:
            icon: 'pause'
            style: "tonal"
            theme_font_size: "Custom"
            font_size: "48sp"
            radius: [self.height / 2, ]
            size_hint: None, None
            size: "60dp", "60dp"
            pos_hint: {'center_x': .9,'center_y': .3}
            on_press: root.pause_timer()
        MDIconButton:
            icon: 'restart'
            style: "tonal"
            theme_font_size: "Custom"
            font_size: "48sp"
            radius: [self.height / 2, ]
            size_hint: None, None
            size: "60dp", "60dp"
            pos_hint: {'center_x': .9,'center_y': .3}
            on_press: root.restart_timer()
            
''')


"""
TO DO LIST:
1. DISPLAY TIME PROPERLY # done ? 
2. Countdown Logic # done ?
3. Fix Ui
4. Disable button functions once the timer started
"""

class WindowManager(ScreenManager):
    pass

class HomeScreen(Screen):
    dialog = None
    work_time = 0
    short_break = 0
    long_break = 0
    mode = 1
    cycle = .5
    current_time = NumericProperty(0)
    timer_running = False
    timer_event = None
    # if mode == 1:
    #     test = 137/255,207/255,240/255,1
    # elif mode == 2:
    #     test = 255/255, 0/255, 0/255, .6 # to be fixed later

    test = ListProperty([255/255, 0/255, 0/255, .6])






    def setting_one(self):
        self.work_time = 25 # for testing purposes 
        self.short_break = 5
        self.long_break = 10
        self.update_display()
        print(self.work_time,self.short_break,self.long_break)
    def setting_two(self):
        self.work_time = 50
        self.short_break = 10
        self.long_break = 15
        self.update_display()
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
            self.update_display()
            print(self.work_time, self.short_break, self.long_break)
        except Exception as e:
            print(f'ERROR: {e}')

    def update_time(self, dt):
        # Timer update logic
        if self.current_time > 0:
            print(f'CYCLE: {self.cycle}')
            minutes, seconds = divmod(self.current_time * 60, 60)
            seconds -= 1
            if seconds < 0:
                minutes -= 1
                seconds = 59
            self.current_time = minutes + (seconds / 60)
            
            if self.current_time <= 0:
                # Clock.unschedule(self.update_time)
                self.switch_mode()  # You'll need to implement this method
                print(self.mode) # for debugging
                print(self.current_time) # for debugging
                self.cycle += .5

            # Update display
            self.ids.time_display.text = f'{int(minutes):02}:{int(seconds):02}'

    def update_display(self): # claude generated
        if self.mode == 1:
            self.current_time = self.work_time
            # self.test = (137/255, 207/255, 240/255, 1)  # Blue for work
        elif self.mode == 2:
            self.current_time = self.short_break
            # self.test = (180/255, 240/255, 137/255, 1)  # Green for short break
        elif self.mode == 3:
            self.current_time = self.long_break
            # self.test = (240/255, 137/255, 207/255, 1)  # Purple for long break
        
        self.update_background_color()

        # Convert minutes to the correct format
        minutes = int(self.current_time)
        seconds = int((self.current_time * 60) % 60)
        self.ids.time_display.text = f'{minutes:02}:{seconds:02}'
        self.ids.start_button.disabled = (self.current_time == 0)

    def update_background_color(self):
        if self.mode == 1:
            self.test = [255/255, 0/255, 0/255, .6]  # Red for work
        elif self.mode == 2:
            self.test = [137/255, 207/255, 240/255, 1]
        elif self.mode == 3:
            self.test = [180/255, 240/255, 137/255, 1] # Green for short break


    def switch_mode(self):
        if self.current_time <= 0:
            if self.mode == 1:
                if self.cycle == 4:
                    sound = SoundLoader.load('assets/long_break.ogg')
                    if sound:
                        sound.play()
                    self.mode = 3
                    self.cycle = 0
                else:
                    sound = SoundLoader.load('assets/short_break.ogg')
                    if sound:
                        sound.play()
                    self.mode = 2
            elif self.mode == 2:  
                if self.cycle == 4:
                    sound = SoundLoader.load('assets/long_break.ogg')
                    if sound:
                        sound.play()
                    self.mode = 3
                    self.cycle = 0
                else:
                    sound = SoundLoader.load('assets/work_time.ogg')
                    if sound:
                        sound.play()
                    self.mode = 1 
            elif self.mode == 3:  
                sound = SoundLoader.load('assets/long_break.ogg')
                if sound:
                    sound.play() 
                self.cycle = 0
                self.mode = 1
                    
        self.update_background_color()
        self.update_display()



    def start_timer(self):
        # print(f'TIMER BEFORE: {self.timer_running}')
        # self.timer_running = True
        # print(self.timer_running)
        # print(f'TIMER AFTER: {self.timer_running}')
        print('START')
        Clock.schedule_interval(self.update_time, 1)

    def pause_timer(self):
        print(f'TIMER BEFORE: {self.timer_running}')
        self.timer_running = False
        Clock.unschedule(self.update_time)
        print(f'TIMER AFTER: {self.timer_running}')
        print('PAUSE')

    def restart_timer(self):
        print(f'Time set before: {self.work_time}, {self.short_break}, {self.long_break}')
        Clock.unschedule(self.update_time)
        self.work_time = 0
        self.short_break = 0
        self.long_break = 0
        self.mode = 1
        print(f'Time set after: {self.work_time}, {self.short_break}, {self.long_break}')
        self.update_display()

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
    print('app is running:)')