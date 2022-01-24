#!/usr/bin/python3

import os, platform
if platform.system() == "Linux" or platform.system() == "Darwin":
    os.environ["KIVY_VIDEO"] = "ffpyplayer"

from pysimbotlib.core import PySimbotApp, Robot
from kivy.logger import Logger
from kivy.config import Config


# Force the program to show user's log only for "info" level or more. The info log will be disabled.
Config.set('kivy', 'log_level', 'info')

# update robot every 0.5 seconds (2 frames per sec)
# REFRESH_INTERVAL = 1/5
REFRESH_INTERVAL = 1/10

_count_lim = 0 
_count_set = 0
_ro = 1
_count_stuck = 0
_count_hold = 8

class MyRobot(Robot):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.count = 0

    def update(self):
        global _count_lim, _count_set, _ro, _count_stuck, _count_hold
        # print("Count: {0}".format(_count))
        Logger.info("Smell Angle: {0}".format(self.smell()))
        Logger.info("Distance: {0}".format(self.distance()))
        print("Count_lim:" + str(_count_lim) + " count_set:" + str(_count_set))
        print("ro:" + str(_ro) + " Struck:" + str(_count_stuck))
        # print(self.distance()[0])

        _count_lim = _count_lim + 1  
        
        if (self.distance()[0] >= 5 and self.distance()[1] >= 5 and self.distance()[2] >= 5 and self.distance()[-1] >= 5 and self.distance()[-2] >= 5):
            if (_count_lim >= _count_hold):
                _count_lim = 0
                _count_set = _count_set + 1
                if _count_set < 3:
                    self.turn(self.smell())
            self.move(10)
        
            if (_count_set == 6):
                _ro = _ro * -1
                _count_set = _count_set + 1

            elif (_count_set >= 10):
                self.move(-20)
                self.turn(10)
                _count_set = 0
            else:
                self.move(-10)
                self.turn(30* _ro)
                self.move(10)
        else:
            self.move(-10)
            self.turn(30* _ro)
            self.move(10)

if __name__ == '__main__':
    app = PySimbotApp(robot_cls=MyRobot, num_robots=1, interval=REFRESH_INTERVAL, enable_wasd_control=True)
    app.run()