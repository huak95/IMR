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
import time

odom = np.array([(20, 20, 0),(20, 20, 0)]) # x, y, seta
odom_save = np.array([20, 20, 46.73570458892837]) # x, y, food_seta
odom_count = 0
count = 0

# Force the program to show user's log only for "info" level or more. The info log will be disabled.
Config.set('kivy', 'log_level', 'info')

# update robot every 0.5 seconds (2 frames per sec)
REFRESH_INTERVAL = 1/10

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
        self.closed_dist = 10
        self.hitted_dist = 0
        self.diff_odom = 0

    def update(self):
        global odom, count, odom_save, odom_count
        global _count_lim, _count_set, _ro, _count_stuck, _count_hold, _sum_odom, _sum_odom_pre, _struct, SENSOR, smell_dis
        # _sum_odom_pre = round(sum(odom[0:1],0))

        SENSOR = self.distance()

        # Logger.info("Smell Angle: {0}".format(self.smell()))
        Logger.info("Odom_Now: {0}".format(odom[-1][:]))
        # Logger.info("Odom_Pre: {0}".format(odom[-2][:]))
        # Logger.info("Distance: {0}".format(self.distance()))
        Logger.info("Stuck: {0}".format(self.check_struck()))

        # if count == 0:
        #     self.turn_s(-90)
        #     self.move_s(4)
        # if self.stuck:
        #     self.turn_s(-90)

        # MODE 1 Path finding
        
        odom_count += 1
        if (SENSOR[0] < self.closed_dist):
            self.odom_x_len = odom[-1][0] - odom_save[0]
            Logger.info("odom_x_len: {0}".format(self.odom_x_len))
            print("angle")
            print(odom_save[2])
            self.odom_y_len = np.tan(odom_save[2]*np.pi/180.) * self.odom_x_len
            Logger.info("odom_y_len: {0}".format(self.odom_y_len))
            odom_save = odom[-1] # save
            self.turn_s(90)
            self.odom_go_to_len(self.odom_y_len)

        else:
            self.move_s(5)

        if self.check_struck():
            self.turn_s(15)
            self.move_s(-10)
            self.obstracle_avoid_mode()

        count += 1
    
    def obstracle_avoid_mode(self):
        print("obstracle_avoid_mode ACTIVATE!!")
        global SENSOR
        if(SENSOR[0] >= self.safety_dist and SENSOR[1] >= self.closed_dist and SENSOR[-1] >= self.closed_dist and not self.check_struck()):
            self.move_s(5)

        if(SENSOR[0] >= self.safety_dist and (SENSOR[1] < self.closed_dist) or (SENSOR[-1] < self.closed_dist and not self.check_struck())):
            if (SENSOR[1]<SENSOR[-1]):
                self.turn_s(-5)
            elif(SENSOR[1]>SENSOR[-1]):
                self.turn_s(5)

        if(SENSOR[0] < self.safety_dist and not self.check_struck()):
            self.turn_s(4)

    
    def odom_go_to_len(self, x: int = 0):
        self.odom_arr = np.arange(0,x,5)
        self.odom_arr = np.append(self.odom_arr,[x])
        for i in range(1,len(self.odom_arr)):
            self.odom_arr_cut = self.odom_arr[i] - self.odom_arr[i-1]
            print("self.odom_arr_cut: {0}".format(self.odom_arr_cut))
            self.move_s(self.odom_arr_cut)
            time.sleep(0.0001)

        self.move_s(self.odom_y_len)

    def load_save(self):
        global odom_save, odom, odom_count
        self.turn_s(180)
        self.odom_diff = (odom[-1][0] - odom_save[0])
        print("odom_diff")
        print(self.odom_diff)
        self.move_s(self.odom_diff)
        self.turn_s(180)
        odom_count = 0    
        
        # while True:
        #     if odom[-1] <= odom_save:
        #         break
        #     else:
        #        self.move_s(5)

    # log linear odom data
    def move_s(self, x: int = 0):
        global odom
        if self.check_struck() == False:
            self.move(x)
            self.loc_x = odom[-1][0] + x*np.cos(odom[-1][2] * np.pi /180.)
            self.loc_y = odom[-1][1] + x*np.sin(odom[-1][2] * np.pi /180.)
            self.new_odom_mat = [self.loc_x, self.loc_y, odom[-1][2]]
            odom = np.append(odom, [self.new_odom_mat], axis=0)

    # log angular odom data
    def turn_s(self, x:int = 0):
        global odom
        if self.check_struck() == False:
            self.turn(x)    
            self.loc_z = odom[-1][2] + x 
            self.new_odom_mat = [odom[-1][0], odom[-1][1], self.loc_z]
            odom = np.append(odom, [self.new_odom_mat], axis=0)

    # know the robot actually struck or not
    def check_struck(self):
        global _struct, _count_stuck, odom
        self.diff_odom = np.round(np.average(odom[-2][0:2]) - np.average(odom[-1][0:2]),1)
        # print("diff_odom: {0}".format(self.diff_odom))
        if self.diff_odom <= 1 and self.stuck:
            return True
        else:
            return False
            


if __name__ == '__main__':
    app = PySimbotApp(robot_cls=MyRobot, num_robots=1, interval=REFRESH_INTERVAL, enable_wasd_control=True,save_wasd_history=True)
    app.run()