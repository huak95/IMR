from kivy.config import Config
Config.set('graphics', 'resizable', '0') #0 being off 1 being on as in true/false
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

import os
import platform
from kivy.app import App
from kivy.logger import Logger
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty

from .Simbot import Simbot, PySimbotMap
from .Scaler import Scaler
from .Robot import Robot

from .config import ROBOT_START_POS, DEFAULT_MAP_PATH

class PySimbotApp(App):

    title = 'PySimbot (Created by Saran Khotsathian (Bird), Edited by Chattriya Jariyavajee (Jet) CPE25)'

    def __init__(self,
                robot_cls = Robot,
                num_robots = 1, 
                robot_start_pos = ROBOT_START_POS,
                map_path = DEFAULT_MAP_PATH, 
                interval = 1.0/60.0,
                max_tick = 5000,
                theme = 'default',
                customfn_create_robots = None,
                customfn_before_simulation = None,
                customfn_after_simulation = None,
                enable_wasd_control = False,
                simulation_forever = False,
                food_move_after_eat = True,
                save_wasd_history = False,
                **kwargs):

        super(PySimbotApp, self).__init__(**kwargs)
        Logger.info('Map Path: %s' % map_path)
        self.interval = interval

        Window.size = (900, 600)
        Builder.load_file(map_path)
        if theme == "default":
            Builder.load_file('pysimbotlib/ui/default.kv')
        elif theme == "dark":
            Builder.load_file('pysimbotlib/ui/dark.kv')
        elif theme == "light":
            Builder.load_file('pysimbotlib/ui/light.kv')

        self.simbot = Simbot(max_tick=max_tick,
                            robot_cls = robot_cls, 
                            num_robots = num_robots, 
                            robot_start_pos = robot_start_pos,
                            customfn_create_robots = customfn_create_robots,
                            customfn_before_simulation = customfn_before_simulation,
                            customfn_after_simulation = customfn_after_simulation,
                            simulation_forever = simulation_forever,
                            food_move_after_eat = food_move_after_eat,
                            save_wasd_history = save_wasd_history)
        self.simbotMap = PySimbotMap(self.simbot,
                            enable_wasd_control = enable_wasd_control,
                            save_wasd_history = save_wasd_history)
        self.simbot.add_widget(self.simbotMap, index=1)

    def build(self):
        if platform.system() == 'Darwin':
            self._scaler = Scaler(size=Window.size, scale=2)
            Window.add_widget(self._scaler)
            parent = self._scaler or Window
            parent.add_widget(self.simbot)
        else:
            Window.add_widget(self.simbot)

        Clock.schedule_interval(self.simbot.process, self.interval)