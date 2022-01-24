#!/usr/bin/python3

from os import write
from pysimbotlib.core import PySimbotApp, Robot
from kivy.config import Config
# Force the program to show user's log only for "info" level or more. The info log will be disabled.
Config.set('kivy', 'log_level', 'info')

import random
import pandas as pd
import csv
from matplotlib import pyplot as plt1
from matplotlib import pyplot as plt2
from numpy import savetxt
import numpy as np
global count
count = 0
dataplot1 = []
dataplot2 = []

class RL_Robot(Robot):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        '''
        Using 5 IR sensor and 1 Smell Sensor
        '''
        self.num_state_sensor = 2
        self.num_sensor = 5
        self.smell_labels = ['F', 'L', 'R', 'C']
        self.state_dice = str()

        self.state_key = str()
        self.pre_state_key = str()
        self.pre_action = str()
        self.temp_eat = int(0)

        # Define all state
        # 2^5 * 4^1 = 128 states
        # Define all action
        # Front, Left, Right = 3 action 
        state_index_list = list()
        for i in range(2**self.num_sensor):
            for label in (self.smell_labels):
                state_index_list.append("{0}{1:05b}".format(label,i))

        # print(state_index_list)
        self.Q_table = pd.DataFrame(
            {
                "Front" : [0] * (self.num_state_sensor ** self.num_sensor * len(self.smell_labels)),
                "Left" :  [0] * (self.num_state_sensor ** self.num_sensor * len(self.smell_labels)),
                "Right" : [0] * (self.num_state_sensor ** self.num_sensor * len(self.smell_labels)),
                "Close" : [0] * (self.num_state_sensor ** self.num_sensor * len(self.smell_labels))
            },
            index = state_index_list
        )

        # Set Initial Value
        self.alpha = 0.5
        self.gramma = 0.9
        # print("        Front  Left  Right")
        print("____________________________")
        print("           Q-table          ")
        print(self.Q_table)
        print("____________________________")

        # Write column name for recording the statistics
        global count
        count += 1
        header = ['Time', 'Eat-Count','Collision-Count']
        with open(f'data{count}.csv','w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
        self.decay = 10

    def update(self):
        # Get value from Smell sensor
        # print(np.round(self.distance()[:2]))
        self.closed_yet = self.distance()[0] > 60 and self.distance()[1] > 40 and self.distance()[-1] > 40 and not self.stuck
        # print(f"Closed?: {self.closed_yet}")
        Target = 'C' if (abs(self.smell()) < 10 and self.closed_yet) else 'F' if abs(self.smell()) < 30 else 'L' if self.smell() < -30 else 'R'
        # Get value from IR sensor
        IR = ''.join(['0' if x < 25 else '1' for x in self.distance()[:3] + self.distance()[-2:]])
        self.state_key = Target + IR
        # print(f"State: {self.state_key}")

        ### Choose Action to do ###
        action = str()
        # Exploiation = 90 %
        self.decay *= 0.9995
        print(f"decay: {self.decay}")
        if random.randint(0,9) > self.decay:
            Q_value = self.Q_table.loc[self.state_key].values.tolist()
            index = Q_value.index(max(Q_value))
            # action = "Front" if index == 0 else 'Left' if index == 1 else 'Right'
            action = "Front" if index == 0 else 'Left' if index == 1 else 'Right' if index == 2 else 'Close'
            # print(f"action: {action}")
            # print(index)
        else:
            x1 = random.randint(0,3)
            # action = 'Front' if x1 == 0 else 'Right' 
            action = 'Front' if x1 == 0 else 'Left' if x1 == 1 else 'Right' if x1 ==2 else 'Close'
            # print(f"rand action: {action}")
            pass
        # print(f"Action: {action}")

        ms = 3 # move step
        rs = 5 # rotage step

        ### Initialized self.reward
        self.reward = float(0.0)

        ### Perform Action and Measure self.reward ###
        if action == 'Front':
            self.move(ms)
            self.reward += -1.0 if self.stuck else -0.1
            if (self.eat_count != self.temp_eat):
                self.temp_eat = self.eat_count
                self.reward += 10.0
        elif action == 'Left':
            self.turn(-rs)
            self.reward += -1.0 if self.stuck else -0.1
            self.reward += -0.1 - (abs(self.smell())/180.)
        elif action == 'Right':
            self.turn(+rs+2)
            self.reward += -1.0 if self.stuck else -0.1
            self.reward += -0.1 - (abs(self.smell())/180.)
        # elif action == 'Close':
        #     self.move(ms)
        #     # if self.closed_yet:
        #     self.turn((self.smell()*0.1))
        #     self.reward += -1.0 if self.stuck else -0.1
        #     if (self.eat_count != self.temp_eat):
        #         self.temp_eat = self.eat_count
        #         self.reward += 10.0

        ### Update Q-Table ###
        # For Initilization is diffrence
        self.pre_state_key = self.state_key if self.pre_state_key == '' else self.pre_state_key
        self.pre_action = action if self.pre_action == '' else self.pre_action
        
        # print(f"pre-action: {self.pre_action}")
        self.maxQ = ( self.Q_table.loc[self.pre_state_key].max(axis=0))
        self.Q1 = (self.Q_table.loc[[self.pre_state_key],[self.pre_action]])
        # print(f"a: {self.var_a}\t b: {self.var_b}")

        self.Q_table.loc[[self.pre_state_key],[self.pre_action]] += \
            self.alpha * (self.reward + self.gramma*self.maxQ - self.Q1)  \

        ### Setting a new pre-state
        self.pre_state_key = self.state_key
        self.pre_action = action

        # if self.stuck:
        #     Deg = random.randint(0, 10)
        #     self.turn(Deg)
        #     self.move(-5)

        # if self.stuck:
        #     self.count_stuck += 1


        ### Write Q-Table to csv
        if self._sm.iteration % 500 == 0 or self._sm.iteration <= 1:
            self.Q_table.to_csv(f'Q-Table_Iter/Q-Table_iter_{self._sm.iteration}.csv', encoding='utf-8')

            # if (self.step % 1000 == 0) and (self.step > 0):
            dataplot1.append(self.eat_count/self._sm.iteration)
            dataplot2.append(self.collision_count/self._sm.iteration)
            # self.step += 1    

            print(f"Eat: {self.eat_count} \t Coll: {self.collision_count} \t Rwd: {round(self.reward,2)}")
            # print(f"Eat: {self.eat_count} \t Coll: {self.collision_count}")
            data = np.round(np.array([self._sm.iteration, self.eat_count/self._sm.iteration, self.collision_count/self._sm.iteration]),3)
            with open(f'data{count}.csv', 'a', encoding='UTF8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(data)
        pass

        # r = random.randint(0, 3)
        # self.move(5)
        # if r == 1:
        #     self.turn(15)
        # elif r == 2:
        #     self.turn(-15)

if __name__ == '__main__':
    app = PySimbotApp(robot_cls=RL_Robot, num_robots=1 \
    , max_tick=100000, interval=1/60.0, enable_wasd_control = True,)
    app.run()
                
    ## Ploting ##
    plt1.plot(dataplot1)
    savetxt("Plot/eat_count.csv",dataplot1)
    plt1.savefig("Plot/eat_count.svg", dpi=150)
    plt1.savefig("Plot/eat_count.png", dpi=150)
    
    plt2.plot(dataplot2)
    savetxt("Plot/collision_count.csv",dataplot2)
    plt2.savefig("Plot/collision_count.svg", dpi=150)
    plt2.savefig("Plot/collision_count.png", dpi=150)