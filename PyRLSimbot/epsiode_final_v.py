#!/usr/bin/python3
'''
Reinforcement Learning FINAL VERSION by Saksorn Ruangtanusak and Sivakorn Sansawas (Both Mechanical Engineer)

ในงาน RL ครั้งนี้ผมเจอจุดอ่อนของโค้ดที่พี่โชว์ให้ดูก็คือ การที่ไม่มีค่า Epsilon-Greedy Decay ที่จะทำให้หุ่นยนต์นั้นมีตาราง Q-Table 
ที่จะใช้เวลาในการทำให้ค่าสมบูรณ์นั้นนานมาก ผมจึงลองทำ Epsilon-Greedy Decay Algorithm ขึ้นมาให้มัน Explore เยอะๆในช่วงแรก
แล้วค่อย Exploitation เมื่อตาราง Q-Table เริ่มดีแล้ว โดยวิธีนี้ได้ผลดีมาก และ สามารถทำงานได้อย่างรวดเร็ว นอกจากนี้ผมได้ใช้ 5 Action 
โดยที่เพิ่มมาคือ Close ไกล้อาหารโดยให้พุ่งไปหาอาหาร แล้วอีก Action คือ Back ให้สามารถเดินถอยหลังเมื่อชนกำแพงได้ 
ผลที่ได้ค่อนข้างดีโดยสามารถหลบสิ่งกีดขวางได้เองตอนช่วงหลัง

5 IR sensor [0,1,2,-1,-2] with 2 level [near, far] + 1 smell sensor
5 Action (Front, Left, Right, Close, Back)

Initial parameter alpha = 0.5, gamma = 0.9, 
Initial Epsilon = 1.0, Decay per Episodes = 0.99
'''
from os import write

from pandas.core.indexes import interval
from pysimbotlib.core import PySimbotApp, Robot
from kivy.config import Config
# Force the program to show user's log only for "info" level or more. The info log will be disabled.
Config.set('kivy', 'log_level', 'info')

import os 
import shutil
import random
import pandas as pd
import csv
from matplotlib import pyplot as plt
import matplotlib.animation as anime
from numpy import savetxt
import numpy as np
global count
count = 0
dataplot1 = []
dataplot2 = []

fig = plt.figure(figsize=[15,6])
ax1 = fig.add_subplot(1,2,1)
ax2 = fig.add_subplot(1,2,2)

print("""
  _____      _        __                                        _     _                           _             
 |  __ \    (_)      / _|                                      | |   | |                         (_)            
 | |__) |___ _ _ __ | |_ ___  _ __ ___ ___ _ __ ___   ___ _ __ | |_  | |     ___  __ _ _ __ _ __  _ _ __   __ _ 
 |  _  // _ \ | '_ \|  _/ _ \| '__/ __/ _ \ '_ ` _ \ / _ \ '_ \| __| | |    / _ \/ _` | '__| '_ \| | '_ \ / _` |
 | | \ \  __/ | | | | || (_) | | | (_|  __/ | | | | |  __/ | | | |_  | |___|  __/ (_| | |  | | | | | | | | (_| |
 |_|  \_\___|_|_| |_|_| \___/|_|  \___\___|_| |_| |_|\___|_| |_|\__| |______\___|\__,_|_|  |_| |_|_|_| |_|\__, |
                                                                                                           __/ |
                                                                                                          |___/ 
BY SAKSORN RUANGTANUSAK and SIVAKORN SANSAWAS
                                                                                                          """)
class RL_Robot(Robot):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        '''
        Using 5 IR sensor and 1 Smell Sensor
        '''
        self.num_state_sensor = 2
        self.num_sensor = 5
        self.smell_labels = ['F', 'L', 'R', 'C', 'B']
        self.state_dice = str()

        self.state_key = str()
        self.pre_state_key = str()
        self.pre_action = str()
        self.temp_eat = int(0)

        # Define all state
        # 2^5 * 5^1 = 160 states
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
                "Close" : [0] * (self.num_state_sensor ** self.num_sensor * len(self.smell_labels)),
                "Back" : [0] * (self.num_state_sensor ** self.num_sensor * len(self.smell_labels))
            },
            index = state_index_list
        )

        # Set Initial Value
        self.alpha = 0.5
        self.gramma = 0.9
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
        
        shutil.rmtree("Q-Table_Iter")
        os.mkdir("Q-Table_Iter")
        self.epsilon = 1.0

    def episode_loop(self):
        # Get value from Smell sensor
        self.closed_yet = self.distance()[0] > 60 and self.distance()[1] > 40 and self.distance()[-1] > 40 and not self.stuck
        Target = 'C' if (abs(self.smell()) < 10 and self.closed_yet) else 'F' if abs(self.smell()) < 30 else 'L' if self.smell() < -30 else 'R'
        # Get value from IR sensor
        IR = ''.join(['0' if x < 35 else '1' for x in self.distance()[:3] + self.distance()[-2:]])
        self.state_key = Target + IR
        # print(f"State: {self.state_key}")

        ### Choose Action to do ###
        action = str()
        if random.randint(0,9)*0.1 < self.epsilon:
            ### EXPLORE (Random) ###
            x1 = random.randint(0,4)
            action = 'Front' if x1 == 0 else 'Left' if x1 == 1 else 'Right' if x1 ==2 else 'Close' if x1 ==3 else 'Back'
            pass
        else:
            ### EXPLOIT (Use Q-Table) ###
            Q_value = self.Q_table.loc[self.state_key].values.tolist()
            index = Q_value.index(max(Q_value))
            action = "Front" if index == 0 else 'Left' if index == 1 else 'Right' if index == 2 else 'Close' if index == 3 else 'Back'

        ms = 5 # move step
        rs = 5 # rotage step

        ### Initialized self.reward
        self.reward = float(0.0)

        ### Perform Action and Measure self.reward ###
        if action == 'Front':
            self.move(ms)
            self.reward += -1.0 if self.stuck else 0.2
        elif action == 'Left':
            self.turn(-rs-1)
            self.reward += -2.0 if self.stuck else 0.2
            self.reward += -0.1 - (abs(self.smell())/180.)
        elif action == 'Right':
            self.turn(+rs-1)
            self.reward += -2.0 if self.stuck else 0.2
            self.reward += -0.1 - (abs(self.smell())/180.)
        elif action == 'Close':
            if self.closed_yet:
                self.move(ms-2)
                self.turn((self.smell()*self.epsilon/2.))
                self.reward += -1.0 if self.stuck else 0.2
            if (self.eat_count != self.temp_eat):
                self.temp_eat = self.eat_count
                self.reward += 10.0
                self.turn((self.smell()*self.epsilon/2.))
        elif action == 'Back' and self.stuck:
            for i in range(5): self.turn(30)
            self.move(3)
            self.reward += -2.0 

        ### Update Q-Table ###
        # For Initilization is diffrence
        self.pre_state_key = self.state_key if self.pre_state_key == '' else self.pre_state_key
        self.pre_action = action if self.pre_action == '' else self.pre_action
        
        self.maxQ = ( self.Q_table.loc[self.pre_state_key].max(axis=0))
        self.Q1 = (self.Q_table.loc[[self.pre_state_key],[self.pre_action]])

        self.Q_table.loc[[self.pre_state_key],[self.pre_action]] += \
            self.alpha * (self.reward + self.gramma*self.maxQ - self.Q1)  \

        ### Setting a new pre-state
        self.pre_state_key = self.state_key
        self.pre_action = action

        ### Write Q-Table to csv
        if self._sm.iteration % 1000 == 0 or self._sm.iteration <= 1:
            self.Q_table.to_csv(f'Q-Table_Iter/Q-Table_iter_{self._sm.iteration}.csv', encoding='utf-8')

            # if (self.step % 1000 == 0) and (self.step > 0):
            dataplot1.append(self.eat_count/self._sm.iteration)
            dataplot2.append(self.collision_count/self._sm.iteration)
            savetxt("Plot/eat_count.csv",dataplot1)
            savetxt("Plot/collision_count.csv",dataplot2)   

            print(f"Eat: {self.eat_count} \t Coll: {self.collision_count} \t Rwd: {round(self.reward,2)}")
            # print(f"Eat: {self.eat_count} \t Coll: {self.collision_count}")
            data = np.round(np.array([self._sm.iteration, self.eat_count/self._sm.iteration, self.collision_count/self._sm.iteration]),3)
            with open(f'data{count}.csv', 'a', encoding='UTF8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(data)
        pass

    def plot_fn1(self):
        ax1.plot(dataplot1)
        ax1.set_title("eat_count")
        ax2.plot(dataplot2)
        ax2.set_title("collision_count")
        fig.savefig("Plot/plot_run.svg", dpi=150)
        fig.savefig("Plot/plot_run.png", dpi=150)

    def update(self):
        self.episode_loop()
        if self._sm.iteration % 1000 == 0:
            if self.epsilon <= 0.1:
                self.epsilon = 0.1
            else: 
                self.epsilon *= 0.99
            print(f"decay: {self.epsilon}")
        if self._sm.iteration % 10000 == 0:
            self.plot_fn1()
            pass

if __name__ == '__main__':
    app = PySimbotApp(robot_cls=RL_Robot, num_robots=1 \
    , max_tick=300000, interval=1/360.0, enable_wasd_control = True,)
    app.run()
    ax1.plot(dataplot1)
    ax1.set_title("eat_count")
    ax2.plot(dataplot2)
    ax2.set_title("collision_count")
    fig.savefig("Plot/plot.svg", dpi=150)
    fig.savefig("Plot/plot.png", dpi=150)
    plt.show()