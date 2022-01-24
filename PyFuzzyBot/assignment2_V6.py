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

# Force the program to show user's log only for "info" level or more. The info log will be disabled.
Config.set('kivy', 'log_level', 'info')
# START POINT
START_POINT = (20, 560)

# update robot every 0.5 seconds (2 frames per sec)
REFRESH_INTERVAL = 1/15
count = 1
rotage_var = 1
count_struck = 0

class MyRobot(Robot):

    def __init__(self):
        super(MyRobot, self).__init__()
        self.pos = START_POINT

    def update(self):
        global count, rotage_var, count_struck
        ''' Update method which will be called each frame
        '''        
        self.ir_values = self.distance()
        self.target = self.smell()
        Logger.info("Distance: {0}".format(self.distance()))
        Logger.info("Stuck: {0}".format(self.stuck))

        # initial list of rules
        rules = list()
        turns = list()
        moves = list()

        # __move forward when front is far__

        rules.append(self.far_ir(0) * self.far_ir(-2) * self.far_ir(2))
        moves.append(15)
        turns.append(0)

        rules.append(self.far_ir(0)* np.min([self.near_ir(-2),self.near_ir(2)]))
        moves.append(8)
        turns.append(0)

        rules.append(self.near_ir(0))
        moves.append(3)
        turns.append(0)
        
        # __move back for safety__
        rules.append(self.near_ir(0))
        moves.append(-5)
        turns.append(0)

        rules.append(self.near_ir(0) * self.near_ir(-1) * self.near_ir(1))
        moves.append(-8)
        turns.append(5)

        rules.append(self.stuck * np.max([self.mid_ir(0), self.mid_ir(1),self.mid_ir(-1)]) )
        moves.append(0)
        turns.append(180)

        # back sensor
        rules.append(self.near_ir(3) * self.near_ir(4) * self.near_ir(5) * self.far_ir(0))
        moves.append(3)
        turns.append(0)

        # right sensor 
        rules.append(self.near_ir(-2) * self.far_ir(2))
        moves.append(3)
        turns.append(20)
        
        rules.append(self.near_ir(-1) * self.far_ir(1))
        moves.append(3)
        turns.append(10)

        # left sensor
        rules.append(self.far_ir(-2) * self.near_ir(2))
        moves.append(3)
        turns.append(-20)

        rules.append(self.far_ir(-1) * self.near_ir(1))
        moves.append(3)
        turns.append(-10)

        # __________FOOD RULE__________

        # smell center move
        rules.append(self.smell_center() * self.far_ir(0) )
        moves.append(10)
        turns.append(0)

        rules.append(self.smell_center() * np.min([self.far_ir(-2), self.far_ir(2), self.near_ir(0) ]))
        moves.append(-20)
        turns.append(10)

        rules.append(self.smell_left() * self.far_ir(0) * np.min([self.far_ir(-2), self.far_ir(2)]))
        moves.append(0)
        turns.append(-12)

        rules.append(self.smell_right() * self.far_ir(0) * np.min([self.far_ir(-2), self.far_ir(2)]))
        moves.append(0)
        turns.append(15)
        
        rules.append(self.smell_back() * self.far_ir(4) * self.far_ir(0))
        moves.append(0)
        turns.append(180)

        # ________FIX STRUCK_______
        if count % 20 == 0:
            rules.append(0.5)
            moves.append(-3)
            turns.append(10)

        # if count % 120 == 0:
        #     rules.append(1.0)
        #     moves.append(-5)
        #     turns.append(-120)
            # turns.append(10*rotage_var)
            # count_struck += 1

        # elif count_struck >= 30:
        #     rotage_var = -1 

        # elif count_struck >= 50:
        #     rotage_var = 2 
        #     count_struck = 0

        ans_turn = 0.0
        ans_move = 0.0
        for r, t, m in zip(rules, turns, moves):
            ans_turn += t * r
            ans_move += m * r

        self.turn(int(ans_turn))
        self.move(int(ans_move))

        count += 1
    
    def near_ir(self, x):
        self.ir = self.ir_values[x]
        if x%2 == 0:
            self.x1 = 8.0
            self.x2 = 40.0
        else:
            self.x1 = 14.0
            self.x2 = 30.0

        if self.ir <= self.x1:
            return 1.0
        elif self.ir >= self.x2:
            return 0.0
        else:
            return (self.ir-self.x1)/(self.x2-self.x1)

    def mid_ir(self, x):
        self.ir = self.ir_values[x]       
        self.x1 = 10.0
        self.x2 = 20.0
        self.x3 = 40.0
        if self.ir <= self.x1:
            return 0.0
        elif self.ir > self.x1 and self.ir < self.x2:
            return (self.ir-self.x1)/(self.x2-self.x1)
        elif self.ir >= self.x2 and self.ir < self.x3:
            return 1.0 - (self.ir-self.x2)/(self.x3-self.x2)
        else:
            return 0.0

    def far_ir(self, x):
        return 1.0 - self.near_ir(x)
    
    def smell_right(self):
        target = self.smell()
        LB = 5
        RB = 135
        if target <= LB:
            return 0.0
        elif target >= RB:
            return 1.0
        else:
            return abs((RB-target) / (RB-LB))

    def smell_center(self):
        target = self.smell()
        LB = -15
        MB = 0
        RB = 15
        if target >= LB:
            return 0.0
        elif target == MB:
            return 1.0
        elif target <= RB:
            return 0.0
        elif target>MB and target < RB:
            return abs((target-MB) / (RB-MB))
        elif target<MB and target > LB:
            return abs((target-MB) / (LB-MB))

    def smell_left(self):
        target = self.smell()
        LB = -135
        RB = -5
        if target <= LB:
            return 1.0
        elif target >= RB:
            return 0.0
        else:
            return abs((target-RB) / (LB-RB))

    def smell_back(self):
        target = self.smell()
        LB = -135
        MB = 180
        RB = 135
        if target >= LB:
            return 0.0
        elif target == MB:
            return 1.0
        elif target <= RB:
            return 0.0
        elif target>MB and target < RB:
            return abs((target-MB) / (RB-MB))
        elif target<MB and target > LB:
            return abs((target-MB) / (LB-MB))


if __name__ == '__main__':
    app = PySimbotApp(map="default", robot_cls=MyRobot, num_robots=1, interval=REFRESH_INTERVAL, enable_wasd_control=True,save_wasd_history=True)
    app.run()