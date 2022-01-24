#!/usr/bin/python3

import os, platform

from kivy.app import App
from numpy.core.defchararray import count
if platform.system() == "Linux" or platform.system() == "Darwin":
    os.environ["KIVY_VIDEO"] = "ffpyplayer"

from pysimbotlib.core import PySimbotApp, Robot, Simbot
from kivy.logger import Logger
from kivy.config import Config
import numpy as np

odom = np.array([(20, 20, 0),(20, 20, 0)]) # x, y, seta

count = 0

# Force the program to show user's log only for "info" level or more. The info log will be disabled.
Config.set('kivy', 'log_level', 'info')

# update robot every 0.5 seconds (2 frames per sec)
REFRESH_INTERVAL = 1/4

_count_lim = 0 
_count_set = 0
_ro = 1
_count_stuck = 0
_count_hold = 8
_sum_odom = 0
_sum_odom_pre = 0
_struct = 0
SENSOR = [0]*8
smell_dis =0 

class MyRobot(Robot):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.safety_dist = 30
        self.closed_dist = 5
        self.hitted_dist = 0

    def update(self):
        global odom, count
        global _count_lim, _count_set, _ro, _count_stuck, _count_hold, _sum_odom, _sum_odom_pre, _struct, SENSOR, smell_dis
        # _sum_odom_pre = round(sum(odom[0:1],0))

        Logger.info("Smell Angle: {0}".format(self.smell()))
        Logger.info("Odom_Now: {0}".format(odom[0][:]))
        Logger.info("Odom_Pre: {0}".format(odom[1][:]))
        Logger.info("Distance: {0}".format(self.distance()))
        Logger.info("Stuck: {0}".format(self.check_struck()))

        # if count == 0:
        #     self.turn_s(-90)
        #     self.move_s(4)
        # if self.stuck:
        #     self.turn_s(-90)

        self.move_s(3)
        
        smell_dis = self.smell_nearest()
        SENSOR = self.distance()
        
        _count_lim = _count_lim + 1  
        
        if (SENSOR[0] >= self.safety_dist and SENSOR[1] >= self.safety_dist and SENSOR[-1] >= self.safety_dist):
            self.move_s(3)
            if self.smell()>0:
                self.turn_s(10)
            else:
                self.turn_s(-10)

        if(SENSOR[0] >= self.safety_dist and SENSOR[1] >= self.closed_dist and SENSOR[-1] >= self.closed_dist):
            self.move_s(5)

        if(SENSOR[0] >= self.safety_dist and (SENSOR[1] < self.closed_dist) or (SENSOR[-1] < self.closed_dist)):
            if (SENSOR[1]<SENSOR[-1]):
                self.turn_s(-5)
            elif(SENSOR[1]>SENSOR[-1]):
                self.turn_s(5)

        if(SENSOR[0] < self.safety_dist):
            self.turn_s(4*_ro)

        # _sum_dist = _sum_dist + smell_dis
        # if _count_lim%3 == 0:
        #    _sum_dist = 0
                   
        if (_count_stuck > 10):
            _ro = _ro * -1
            self.move_s(-5)
            self.turn_s(-odom[2])
            _count_stuck = 0

        count += 1

    # log linear odom data
    def move_s(self, x: int = 0):
        global odom
        odom[1][0] = odom[0][0]
        odom[1][1] = odom[0][1]
        if self.check_struck() == False:
            self.move(x)
            odom[0][0] += x*np.cos(odom[0][2] * np.pi /180.)
            odom[0][1] += x*np.sin(odom[0][2] * np.pi /180.)

    # log angular odom data
    def turn_s(self, x:int = 0):
        global odom
        odom[1][2] = odom[0][2]
        if self.check_struck() == False:
            self.turn(x)    
            odom[0][2] += x

    # know the robot actually struck or not
    def check_struck(self):
        global _struct, _count_stuck, odom
        self.diff_odom = sum(odom[0][0:2]) - sum(odom[1][0:2])
        # Logger.info("diff_odom: {0}".format(self.diff_odom))

        if self.diff_odom <= 2 and self.stuck:
            return True
        else:
            return False
            


if __name__ == '__main__':
    app = PySimbotApp(robot_cls=MyRobot, num_robots=1, interval=REFRESH_INTERVAL, enable_wasd_control=True,save_wasd_history=True)
    app.run()