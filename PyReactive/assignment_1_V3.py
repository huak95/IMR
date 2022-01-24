#!/usr/bin/python3
# This is very simple 

import os, platform
if platform.system() == "Linux" or platform.system() == "Darwin":
    os.environ["KIVY_VIDEO"] = "ffpyplayer"

from pysimbotlib.core import PySimbotApp, Robot
from kivy.logger import Logger
from kivy.config import Config

# Force the program to show user's log only for "info" level or more. The info log will be disabled.
Config.set('kivy', 'log_level', 'info')

angle = 0
turn_deg = 0
SENSOR = [0]*8
# update robot every 0.5 seconds (2 frames per sec)
REFRESH_INTERVAL = 1/20
safety_dist = 20
closed_dist = 3


class MyRobot(Robot):
    
    def update(self):
        global angle, SENSOR, turn_deg,safety_dist, closed_dist
        Logger.info("Smell Angle: {0}".format(self.smell()))
        Logger.info("Distance: {0}".format(self.distance()))
        
        angle = self.smell()
        SENSOR = self.distance()
        turn_deg = 3

        self.move(5)
        if angle < 0:
            self.turn(-60)        
        if angle > 0:
            self.turn(60)

        if SENSOR[0] < safety_dist:
            self.turn(90)
            self.move(1)
        elif SENSOR[1] < closed_dist:
            self.turn(turn_deg)
            self.move(1)
        elif SENSOR[2] < closed_dist:
            self.turn(turn_deg)
            self.move(1)
        elif SENSOR[3] < closed_dist:
            self.turn(turn_deg)
            self.move(1)
        elif SENSOR[4] < closed_dist:
            self.turn(turn_deg)
            self.move(1)


if __name__ == '__main__':
    app = PySimbotApp(robot_cls=MyRobot, num_robots=1, interval=REFRESH_INTERVAL, enable_wasd_control=True)
    app.run()