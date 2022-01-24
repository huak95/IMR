#!/usr/bin/python3

from pysimbotlib.core import PySimbotApp, Robot
from kivy.config import Config
from matplotlib import pyplot as plt1
from matplotlib import pyplot as plt2
Config.set('kivy', 'log_level', 'info')

import random
import pandas as pd
#from sqlalchemy import create_engine
dataplot1 = []
dataplot2 = []

class RL_Robot(Robot):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.step = 0
        
    
    def update(self):
        reward = float()

        if (self.step % 1000 == 0) and (self.step > 0):
            dataplot1.append(self.eat_count/self.step)
            dataplot2.append(self.collision_count/self.step)
        self.step += 1
        pass

if __name__ == '__main__':
    app = PySimbotApp(
        robot_cls=RL_Robot, 
        simulation_forever=False,
        max_tick=300000,
        interval=1/1000.0,
        food_move_after_eat=True,
        num_robots=1
        )
    app.run()
    plt1.plot(dataplot1)
    plt1.show()
    plt2.plot(dataplot2)
    plt2.show()