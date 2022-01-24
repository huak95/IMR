#!/usr/bin/python3

from pysimbotlib.core import PySimbotApp, Simbot, Robot, Util
from kivy.logger import Logger
from kivy.config import Config

# # Force the program to show user's log only for "info" level or more. The info log will be disabled.
# Config.set('kivy', 'log_level', 'debug')
Config.set('graphics', 'maxfps', 10)

import pandas as pd
import numpy as np
import random

from typing import Tuple, Dict

def dist_to_label(dist: float) -> str:
    if dist < 10:
        return 'C'
    elif 10 <= dist < 25:
        return 'N'
    elif 25 <= dist < 50:
        return 'M'
    elif 50 <= dist < 75:
        return 'F'
    else:
        return 'L'

def angle_to_label(angle: float) -> str:
    if -10 <= angle <= 10:
        return 'C'
    elif 10 < angle < 45:
        return 'R'
    elif 45 <= angle < 90:
        return 'Z'
    elif 90 <= angle <= 180 or -180 <= angle <= -90:
        return 'B'
    elif -90 < angle <= -45:
        return 'A'
    elif -45 < angle < -10:
        return 'L'

def convert_data(data: pd.DataFrame) -> None:
    data.iloc[:, 0:8] = data.iloc[:, 0:8].applymap(dist_to_label)
    data.iloc[:, 8:9] = data.iloc[:, 8:9].applymap(angle_to_label)

def turnmove_to_class(row) -> None:
    turn = row['turn']
    move = row['move']
    if turn == 5 and move == 0:
        return 'R'
    elif turn == -5 and move == 0:
        return 'L'
    elif turn == 0 and move == 5:
        return 'F'
    elif turn == 0 and move == -5:
        return 'B'
    else:
        raise NotImplementedError()

class NaiveBayes:
    # Learning phase to build the CPT
    def __init__(self, filename: str):
        data = pd.read_csv(filename, sep=',')

        convert_data(data)
        data['action'] = data.apply(turnmove_to_class, axis=1)
        #
        #
        #  put your code here
        #
        #
        
    # find action that gives the highest conditional probability
    def classify(self, input_data: pd.DataFrame) -> str:
        #
        #
        # put your code here
        #
        #
        pass
        # return action


class NBRobot(Robot):

    def __init__(self, **kwarg):
        super(NBRobot, self).__init__(**kwarg)
        # Learning Phase
        self.nb = NaiveBayes('history_all.csv')

    def update(self):
        # read sensor value
        ir_values = self.distance()  # [0, 100]
        angle = self.smell()         # [-180, 180]
        
        # create 2D array of size 1 x 9
        sensor = np.zeros((1, 9))
        
        # set the values of the input sensor
        for i, ir in enumerate(ir_values):
            sensor[0][i] = ir

        ## use this line if the training data is from Jet
        sensor[0][8] = angle

        input_data = pd.DataFrame(sensor)
        convert_data(input_data)

        # inference
        # answerTurn, answerMove = self.nb.classify(input_data)
        # Test Phase
        action = self.nb.classify(input_data)

        answerTurn = (5 if action == 'R' else (-5 if action == 'L' else 0))
        answerMove = (5 if action == 'F' else (-5 if action == 'B' else 0))

        # perform the robot movement
        self.turn(int(answerTurn))
        self.move(answerMove)

        if self.stuck or (answerTurn == 0 and answerMove == 0):
            Deg = random.randint(-10, 10)
            self.turn(Deg)
            self.move(-5)

if __name__ == '__main__':
    app = PySimbotApp(robot_cls=NBRobot, 
                        num_robots=1,
                        max_tick=5000,
                        theme='default',
                        interval = 1.0/60.0,
                        simulation_forever=False)
    app.run()