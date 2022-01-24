#!/usr/bin/python3

from pysimbotlib.core import PySimbotApp
from kivy.logger import Logger

from kivy.config import Config
# Force the program to show user's log only for "info" level or more. The info log will be disabled.
Config.set('kivy', 'log_level', 'info')

import random

if __name__ == '__main__':
    app = PySimbotApp(enable_wasd_control=True, save_wasd_history=True, max_tick=10000, simulation_forever=True)
    app.run()