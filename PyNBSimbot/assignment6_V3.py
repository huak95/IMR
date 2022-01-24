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
    elif turn == 5 and move == 5: 
        return 'FR'
    elif turn == -5 and move == 5:
        return 'FL'
    else:
        raise NotImplementedError()

class NaiveBayes:
    # Learning phase to build the CPT
    def __init__(self, filename: str):
        data = pd.read_csv(filename, sep=',')

        convert_data(data)
        data['action'] = data.apply(turnmove_to_class, axis=1)
        self.action_class = ['R','L','F','B','FR','FL']
        self.dist_class = ['C','N','M','F','L']
        self.angle_class = ['C','R','Z','B','A','L']
        temp_data_mid = dict()
        temp_data2 = dict()
        temp_prop_large = dict()
        sep_data = dict()

        num_train_set = data.count()[0]
        print(f"num_train_set: {num_train_set}")

        # Separate Data into 7 action class
        for sep in self.action_class:
            sep_data[sep] = data[data['action'] == sep]

        for action in self.action_class:
            each_data = sep_data[action]
            amount_data = max(1,sep_data[action].count()[0])
            # print(f"\nClass {action} : {amount_data}")
            
            for i in data.columns[0:9]:
                prob_data = 0.0
                if i == 'angle':
                    for j in self.angle_class:
                        prob_data = each_data[each_data[i]==j].count()[0]/amount_data
                        temp_data2[j] = prob_data ; prob_data = dict()
                else:
                    for j in self.dist_class:
                        prob_data = each_data[each_data[i]==j].count()[0]/amount_data
                        temp_data2[j] = prob_data ; prob_data = dict()
                # print(f"i: {i}")
                temp_data_mid[i]=temp_data2 ; temp_data2 = dict()
            temp_prop_large[action] = temp_data_mid ; temp_data_mid = dict()
        self.frequency_dict = temp_prop_large; temp_prop_large = dict()
        print(f"frequency_dict: \n{self.frequency_dict}")

        # Calculate prob of action class
        self.action_prop = dict()

        for sep in self.action_class:
            self.action_prop[sep] = data[data['action'] == sep].count()[0]/num_train_set
        print(f"self.action_prop: {self.action_prop}")   

        #  put your code here
        #
        #
    # find action that gives the highest conditional probability
    def classify(self, input_data: pd.DataFrame) -> str:
        #
        #
        # put your code here
        prob_all_class = dict()
        # print(f"input_data: \n{input_data}")
        self.sensor_class = ['ir0','ir1','ir2','ir3','ir4','ir5','ir6','ir7','angle']

        for action in self.action_class:
            # print(action)
            multiple_data = float()
            for i in range(len(input_data.columns)):
                # print(f'i: {i}')
                value_prob = max(0.01, self.frequency_dict[action][self.sensor_class[i]][input_data.iloc[0][i]])
                # print(f"value_prob: {value_prob}")

                # Multiple All Prop
                if multiple_data == 0.0:
                    multiple_data = value_prob
                else:
                    multiple_data *= value_prob
            multiple_data *= self.action_prop[action]

            prob_all_class.update({
                action : multiple_data
            })

        # Finding Max and get action
        action = max((v,k) for k,v in prob_all_class.items())[1]
        # print(f"input_data: \n{input_data.iloc[0][8]} \n{input_data}")
        print(f"action: {action} \t angle: {input_data.iloc[0][8]}")
        # action = 'F'
        return action

class NBRobot(Robot):

    def __init__(self, **kwarg):
        super(NBRobot, self).__init__(**kwarg)
        # Learning Phase
        file_name = "_bb"
        self.nb = NaiveBayes('history' + file_name + ".csv")

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

        answerTurn = (5 if action == 'R' or action == 'FR' else (-5 if action == 'L' else 0))
        answerMove = (5 if action == 'F' or action == 'FR' or action == 'FL' else (-5 if action == 'B' else 0))

        # perform the robot movement
        self.turn(int(answerTurn))
        self.move(int(answerMove))

        if self.stuck or (answerTurn == 0 and answerMove == 0):
            Deg = random.randint(0, 10)
            self.turn(Deg)
            self.move(-8)

if __name__ == '__main__':
    app = PySimbotApp(robot_cls=NBRobot, 
                        num_robots=1,
                        max_tick=10000,
                        theme='default',
                        interval = 1.0/120.0,
                        simulation_forever=False)
    app.run()