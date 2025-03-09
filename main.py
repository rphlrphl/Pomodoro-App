from kivy.uix.accordion import BooleanProperty
from kivy.uix.filechooser import string_types
from kivy.uix.accordion import ListProperty
from kivy.uix.accordion import NumericProperty
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import *
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
import platform
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.utils import platform
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.lang.builder import Builder
from kivy.properties import NumericProperty, ListProperty, BooleanProperty
from kivy.clock import Clock
from kivy.core.audio import SoundLoader

if platform == 'android':
    # Window.size = (480,800)
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.READ_EXTERNAL_STORAGE,Permission.READ_MEDIA_AUDIO])   

Builder.load_string('''
<HomeScreen>:
    canvas.before:
        Color:
            id: background
            rgba: root.bg_color  # Light gray background color
        Rectangle:
            pos: self.pos
            size: self.size    
    MDBoxLayout:
        orientation: 'vertical'
        pos_hint: {'center_y': .9}
        MDLabel:
            text: 'Pomodoable'
            theme_font_name: 'Custom'
            font_name: 'assets/Nexa-Heavy.ttf'
            theme_text_color: 'Custom'
            text_color: 'black'
            font_style: 'Headline'
            role: 'large'
            halign: 'center'

    MDBoxLayout:
        orientation: 'vertical'
        pos_hint: {'center_x': .5,'center_y': 1.2}
        padding: '12dp'
        spacing: '12dp'                         
        MDSegmentedButton:
            size_hint_x: 1
            id: setting_button
            hiding_icon_duration: 0
            MDSegmentedButtonItem:
                id: setting_one
                on_active: root.setting_one()
                MDSegmentButtonLabel:
                    text: '25|5'
            MDSegmentedButtonItem:
                id: setting_two
                on_active: root.setting_two()
                MDSegmentButtonLabel:
                    text: '50|10'
            MDSegmentedButtonItem:
                id: custom_button
                on_active: root.show_custom_time_dialog()
                MDSegmentButtonLabel:
                    text: 'Custom'

    MDBoxLayout:
        halign: 'center'
        MDLabel:
            id: time_display
            text: '00:00'
            theme_font_name: 'Custom'
            font_name: 'assets/THEBOLDFONT.ttf'
            font_style: 'Display'
            role: 'large'
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
            disabled: True
        MDIconButton:
            id: pause_button
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
    work_time = NumericProperty(0)
    short_break = NumericProperty(0)
    long_break = NumericProperty(0)
    mode = NumericProperty(1)
    cycle = NumericProperty(.5)
    current_time = NumericProperty(0)
    timer_running = BooleanProperty(False)
    timer_event = BooleanProperty(None)
    # if mode == 1:
    #     test = 137/255,207/255,240/255,1
    # elif mode == 2:
    #     test = 255/255, 0/255, 0/255, .6 # to be fixed later
    bg_color = ListProperty([220/255,20/255,60/255,1])


    

    def on_kv_post(self, base_widget):
        self.ids.setting_button.selected_item = None

    def disable_buttons(self):
        self.ids.setting_button.disabled = True
        self.ids.start_button.disabled = True

    def enable_buttons(self):
        self.ids.setting_button.disabled = False
        self.ids.start_button.disabled = False

    def enable_one(self):
        self.ids.setting_button.disabled = True
        self.ids.start_button.disabled = False

    def clear_settings(self):
        self.ids.setting_button.selected_item = None
        self.work_time = 0
        self.short_break = 0
        self.long_break = 0
        self.update_display()

    def setting_one(self):
        if not self.ids.setting_one.active:
            return
        
        self.ids.setting_two.active, self.ids.custom_button.active = False, False

        # change later (testing purposes | 25,5,10)
        self.work_time = .05
        self.short_break = .05
        self.long_break = .05
        self.update_display()
        print(self.work_time,self.short_break,self.long_break)

    def setting_two(self):
        if not self.ids.setting_two.active:
            return
        
        self.ids.setting_one.active, self.ids.custom_button.active = False, False

        self.work_time = 50
        self.short_break = 10
        self.long_break = 15
        self.update_display()
        print(self.work_time,self.short_break,self.long_break)

    def show_custom_time_dialog(self):
        if not self.ids.custom_button.active:
            return
        
        self.ids.setting_one.active, self.ids.setting_two.active = False, False

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
                ),
                auto_dismiss=False
            )
            self.dialog.open()

    def close_dialog(self, obj):
        self.ids.custom_button.active = False
        self.ids.start_button.disabled = True
        self.clear_settings()
        self.dialog.dismiss()
        self.dialog = None

    def set_custom_time(self, obj):
        if not all([self.custom_work_time.text, 
                   self.custom_break_time.text, 
                   self.custom_long_break_time.text]):
            # Show error state for empty fields
            if not self.custom_work_time.text:
                self.custom_work_time.error = True
            if not self.custom_break_time.text:
                self.custom_break_time.error = True
            if not self.custom_long_break_time.text:
                self.custom_long_break_time.error = True
            return

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
            
            
            self.ids.time_display.text = f'{int(minutes):02}:{int(seconds):02}'

            if self.current_time <= 0:
                self.switch_mode()  # You'll need to implement this method
                print(self.mode) # for debugging
                print(self.current_time) # for debugging
                self.cycle += .5
            
    def update_display(self):
        if self.mode == 1:
            self.current_time = self.work_time
            # self.test = (137/255, 207/255, 240/255, 1)  # Blue for work
        elif self.mode == 2:
            self.current_time = self.short_break
            # self.test = (180/255, 240/255, 137/255, 1)  # Green for short break
        elif self.mode == 3:
            self.current_time = self.long_break
            # self.test = (240/255, 137/255, 207/255, 1)  # Purple for long break
        
        minutes = int(self.current_time)
        seconds = int((self.current_time * 60) % 60)
        self.update_background_color()

        # Convert minutes to the correct format
        minutes = int(self.current_time)
        seconds = int((self.current_time * 60) % 60)
        self.ids.time_display.text = f'{minutes:02}:{seconds:02}'
        self.ids.start_button.disabled = (self.current_time == 0) or (self.timer_running == True)

    def update_background_color(self):
        if self.mode == 1:
            self.bg_color = [220/255,20/255,60/255,1]
        elif self.mode == 2:
            self.bg_color = [137/255, 207/255, 240/255, 1] #
        elif self.mode == 3:
            self.bg_color = [180/255, 240/255, 137/255, 1]

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
        self.timer_running = True
        self.disable_buttons()
        print('START')
        Clock.schedule_interval(self.update_time, 1)
        
    def pause_timer(self):
        self.timer_running = False
        print(f'TIMER BEFORE: {self.timer_running}')
        self.timer_running = False
        Clock.unschedule(self.update_time)
        print(f'TIMER AFTER: {self.timer_running}')
        print('PAUSE')
        self.enable_one()

    def restart_timer(self):
        self.timer_running = False
        self.ids.setting_one.active, self.ids.setting_two.active, self.ids.custom_button.active = False, False, False
        print(f'Time set before: {self.work_time}, {self.short_break}, {self.long_break}')
        Clock.unschedule(self.update_time)
        self.work_time = 0
        self.short_break = 0
        self.long_break = 0
        self.mode = 1
        print(f'Time set after: {self.work_time}, {self.short_break}, {self.long_break}')
        self.enable_buttons()
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
