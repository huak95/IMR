#!/usr/bin/python3

from pysimbotlib.core import PySimbotApp, Simbot, Robot, Util
from kivy.logger import Logger
from kivy.config import Config
import tensorflow as tf
import random
import numpy as np

# # Force the program to show user's log only for "info" level or more. The info log will be disabled.
# Config.set('kivy', 'log_level', 'debug')
Config.set('graphics', 'maxfps', 10)

# 1. define scaling function
from typing import Tuple
def scale(data, from_interval: Tuple[float, float], to_interval: Tuple[float, float]=(0, 1)):
    from_min, from_max = from_interval
    to_min, to_max = to_interval
    scaled_data = to_min + (data - from_min) * (to_max - to_min) / (from_max - from_min)
    return scaled_data


# 2. create robot for testing the model.
class NNRobot(Robot):

    def __init__(self, **kwarg):
        super(NNRobot, self).__init__(**kwarg)
        self.model = tf.keras.models.load_model('assignment5_model')

    def update(self):
        # read sensor value
        ir_values = self.distance()  # [0, 100]
        angle = self.smell()         # [-180, 180]
        
        # create 2D array of size 1 x 9
        sensor = np.zeros((1, 9))
        
        # set the values of the input sensor
        for i, ir in enumerate(ir_values):
            sensor[0][i] = scale(ir, (0, 100), (0, 1))

        ## use this line if the training data is from Jet
        sensor[0][8] = scale(angle, (-180, 180), (0, 1))

        # inference
        output = self.model.predict(sensor)

        # scale the output back
        answerTurn = scale(output[0][0], (0, 1), (-90, 90))
        answerMove = scale(output[0][1], (0, 1), (-10, 10))

        # perform the robot movement
        self.turn(int(answerTurn))
        self.move(answerMove)

        if self.stuck:
            Deg = random.randint(-10, 10)
            self.turn(Deg)
            self.move(-5)


# 3. start the simulation
if __name__ == '__main__':
    app = PySimbotApp(robot_cls=NNRobot, 
                        num_robots=1,
                        theme='default',
                        interval = 1.0/60.0,
                        simulation_forever=False)
    app.run()