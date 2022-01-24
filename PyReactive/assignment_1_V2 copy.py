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
REFRESH_INTERVAL = 1/5

_count_lim = 0 
_count_set = 0
_ro = 1
_count_stuck = 0
_count_hold = 8
_sum_dist = 0
_sum_dist_pre = 0
_struct = 0
SENSOR = [0]*8
smell_dis =0 
turn_deg = 90
class MyRobot(Robot):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.safety_dist = 25
        self.closed_dist = 6
        self.hitted_dist = 0

    def update(self):
        global _count_lim, _count_set, _ro, _count_stuck, _count_hold, _sum_dist, _sum_dist_pre, _struct, SENSOR, smell_dis, turn_deg

        _sum_dist_pre = round(sum(self.distance()),0)

        # print("Count: {0}".format(_count))
        Logger.info("Smell Angle: {0}".format(self.smell()))
        Logger.info("Distance: {0}".format(self.distance()))
        print("Count_lim:" + str(_count_lim) + " count_set:" + str(_count_set))
        print("_struct " + str(_struct))
        print("_sum_dist_pre " + str(_sum_dist_pre) + " _sum_dist " + str(_sum_dist))
        print("ro:" + str(_ro) + " _count_stuck:" + str(_count_stuck))
        print("smell_dis: {0}".format(self.smell_nearest()))
        # print(self.distance()[0])
        smell_dis = self.smell_nearest()
        SENSOR = self.distance()
        
        _count_lim = _count_lim + 1  

        if _sum_dist_pre == _sum_dist:
            _struct = 1
            _count_stuck = _count_stuck + 1
        else:
            _struct = 0
        
        if (SENSOR[0] >= 40 and SENSOR[1] >= self.safety_dist and SENSOR[-1] >= self.safety_dist):
            self.move(4)
            if self.smell()>0:
                self.turn(turn_deg)
            else:
                self.turn(-turn_deg)

        if(SENSOR[0] >= self.safety_dist and SENSOR[1] >= self.closed_dist and SENSOR[-1] >= self.closed_dist):
            self.move(4)
        
        if(SENSOR[0] >= 100):
            self.move(5)

        if(SENSOR[0] >= self.safety_dist and (SENSOR[1] < self.closed_dist) or (SENSOR[-1] < self.closed_dist)):
            if (SENSOR[1]<SENSOR[-1]):
                self.turn(-turn_deg)
            elif(SENSOR[1]>SENSOR[-1]):
                self.turn(turn_deg)

        if(SENSOR[0] < self.safety_dist):
            self.turn(turn_deg*_ro)

        _sum_dist = _sum_dist + smell_dis
        if _count_lim%3 == 0:
           _sum_dist = 0
                   
        # _sum_dist = round(sum(SENSOR),0)      

        # if (_count_stuck > 10):
        #     _ro = _ro * -1
        #     self.move(-5)
        #     self.turn(10)
        #     self.turn(10)
        #     self.turn(10)
        #     _count_stuck = 0
        

if __name__ == '__main__':
    app = PySimbotApp(robot_cls=MyRobot, num_robots=1, interval=REFRESH_INTERVAL, enable_wasd_control=True)
    app.run()