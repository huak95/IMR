# !/usr/bin/python3

# update robot every 0.5 seconds (2 frames per sec)
REFRESH_INTERVAL = 1/20


import os, platform
import math
from posixpath import lexists
from numpy import lib

from numpy.lib.twodim_base import triu_indices_from
from pysimbotlib.core.Simbot import Simbot
import numpy as np

if platform.system() == "Linux" or platform.system() == "Daself.distance()[2]in":
    os.environ["KIVY_VIDEO"] = "ffpyplayer"

from pysimbotlib.core import PySimbotApp, Robot
from kivy.logger import Logger
from kivy.config import Config
from kivy.core.window import Window
import lidar_env
import lidar_sensors
import pygame
import math
import random

random.seed(8)
# Force the program to show user's log only for "info" level or more. The info log will be disabled.
Config.set('kivy', 'log_level', 'info')
environment = lidar_env.buildEnvironment((600,700))
environment.originalMap = environment.map.copy()
laser = lidar_sensors.LaserSensor(200,environment.originalMap,uncertainty=(0.5,0.01))
environment.map.fill((0,0,0))
environment.infomap = environment.map.copy()
running = True
stuck_count = 0


class MyRobot(Robot):
    global Newturn
    Newturn = 1
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.count = 0

    def update(self):
        global Newturn, stuck_count ,a,b,c
    

    #Lidar System
        def Log():
            Logger.info("Distance: {0}".format(self.distance()))
            #Logger.info("IR[0]: {0}".format(self.distance()[0]))
            #Logger.info("IR[1]: {0}".format(self.distance()[1]))
            #Logger.info("IR[-1]: {0}".format(self.distance()[-1]))
            Logger.info("Robot_Position: {0}".format(self.pos[:]))
            #Logger.info("Object_Position: {0}".format(self.get_obj_location()))
            Logger.info("Current_Robot_Direction: {0}".format(self._direction))
            Logger.info("Smell_Angle: {0}".format(self.smell()))
            #Logger.info("Size: {0}".format(self.size))      
        def lidar():
            sensorON = True
            if sensorON :
                #position=pygame.mouse.get_pos()
                position=(self.pos[0],600-self.pos[1])
                print(position)
                laser.position = position
                sensor_data = laser.sense_obstacles()
                environment.dataStorage(sensor_data)
                environment.show_sensorData()
            environment.map.blit(environment.infomap,(0,0))
            pygame.display.update()
        def Move_update(move_dis):
            global Newturn
            self.move(move_dis)
            position=(self.pos[0],abs(600-self.pos[1]))
            initial_x,initial_y = position[0] , position[1]
            pygame.draw.circle(environment.map, (255, 255, 0), (int(initial_x*10)/10,int(initial_y*10)/10),5)
        def path_direct_planner():
            global map
            position=(self.pos[0],abs(600-self.pos[1]))
            initial_x,initial_y = position[0] , position[1]
            Diag_line = math.sqrt(700**2 + 600**2)
            Diag_ang = -(self._direction+self.smell())
            des_x, des_y = Diag_line*math.cos((Diag_ang )*math.pi/180)+initial_x, Diag_line*-math.sin((Diag_ang )*math.pi/180)+initial_y
            MapDimensions = [600,700]

            print(Diag_ang)
            pygame.init()
            lidar.pointCloud = []
            lidar.externalMap = pygame.image.load('map2.png')
            lidar.maph, lidar.mapw = MapDimensions
            lidar.MapWindowName = 'Anotonomous Path'
            pygame.display.set_caption(lidar.MapWindowName)
            map = pygame.display.set_mode((lidar.mapw, lidar.maph))

            pygame.draw.aaline(map, (255, 255, 0),  (int(des_x), int(des_y)),(int(initial_x),int(initial_y)))
            print(des_x, des_y , initial_x,initial_y)

            x0, y0 = initial_x, initial_y # initial reference create line
            x1, y1 =  des_x, des_y # initial reference create line
            dx, dy = (x1-x0), (y1-y0)
            a = dy/dx
            b = -1
            c = (-dy/dx)*x0 + y0
            return a, b, c  # return abc to fomulate equation  

        def balanceControl(stuck_count,DIS):
            current_pos = np.sum(self.distance()[:])
            _SFT = DIS
            _SA = 5
            if self.stuck:
                Move_update(-10)
            for i in range(0,int(360),_SA):
                    self.turn(-_SA)
                    if self.distance()[0]<_SFT:
                        Move_update(-_SFT)
            if stuck_count >= 10 or self.stuck == True:
                for i in range(0,int(360),_SA):
                    self.turn(_SA)
                    if self.distance()[0]<_SFT:
                        Move_update(-_SFT)
            if np.round(np.sum(self.distance()[:]) == current_pos ):
                stuck_count = stuck_count + 1
            if np.round(np.sum(self.distance()[:]) != current_pos ):
                stuck_count = 0
        def Lidar_system() :
            global Eaten, Newturn,a,b,c
            Log()
            lidar()
            if Newturn > 0 :
                print("Going to run mew path")
                a, b, c  =  path_direct_planner()
                Eaten = self.eat_count
                Newturn = 0
            if Eaten < self.eat_count :
                Newturn = 1

        Lidar_system()
        balanceControl(stuck_count,1)

    #Fuzzy Logic Control
        
    #Fuzzification
        #Smell Angle
        def smell_right(BC):
            LB,RB = BC
            target = self.smell()
            if target <= LB:
                return 0.0
            elif target >= RB:
                return 1.0
            else:
                return abs((RB-target) / (RB-LB))
        def smell_center(BC):
            LB,MB,RB = BC
            target = self.smell()
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
        def smell_left(BC):
            LB,RB = BC
            target = self.smell()
            if target <= LB:
                return 1.0
            elif target >= RB:
                return 0.0
            else:
                return abs((target-RB) / (LB-RB))
        def smell_back(BC):
            LB,MB,RB = BC
            target = self.smell()
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















            # print("Stuck",self.stuck,"Newturn", Newturn, "justeat", int(self.just_eat),"eatcount",self.eat_count,"Stuck_count",stuck_count)

        #Movement
        def near_ir(S,BC):
            LB,RB = BC
            target = self.distance()[S]
            if target <= LB:
                return 1.0
            elif target >= RB:
                return 0.0
            else:
                return abs((target-LB) / (RB-LB))
        def mid_ir(S,BC):
            LB,MB,RB = BC
            target = self.distance()[S]
            if target <= LB:
                return 0.0
            elif target == MB:
                return 1.0
            elif target >= RB:
                return 0.0
            elif target>=MB and target < RB:
                return abs((target-MB) / (RB-MB))
            elif target<=MB and target > LB:
                return abs((target-MB) / (LB-MB))
        def far_ir(S,BC):
            LB,RB = BC
            target = self.distance()[S]
            if target <= LB:
                return 0.0
            elif target >= RB:
                return 1.0
            else:
                return abs((target-LB) / (RB-LB))

    #Interrence
    # initialize list of rules
        rules = list()
        turns = list()
        moves = list()
    # Boundary Condition
        #Movement
        near_BC = [0,10]
        mid_BC = [0,50,100]
        far_BC = [10,50]
        #Turns
        right_BC = [0,90]
        left_BC = [-90,0]
        center_BC = [-10,0,10]
        
    # Rule
    # Move Forward 

    #R1 : Right Smell
        rules.append(min(smell_right(right_BC) ,far_ir(0,far_BC), far_ir(1,far_BC), far_ir(2,far_BC)))
        moves.append(0)
        turns.append(90)
    #R2 : Left smell
        rules.append(min(smell_left(left_BC) ,far_ir(0,far_BC), far_ir(-1,far_BC), far_ir(-2,far_BC)))
        moves.append(0)
        turns.append(-87)
    #R3 : Front Far Then Move 20
        rules.append(far_ir(0,far_BC))
        moves.append(9)
        turns.append(0)

    #R4 : Left far turn Left
        rules.append((far_ir(-2,far_BC)))
        moves.append(0)
        turns.append(-15)
    #R5 : Right far turn Right
        rules.append((far_ir(2,far_BC)))
        moves.append(0)
        turns.append(15)
    #R6 : Left front_far or Righ front near turn Left
        rules.append(max(far_ir(-1,far_BC),near_ir(1,near_BC)))
        moves.append(0)
        turns.append(-44)
    #R7 : Left front_near or Righ front far turn Right
        rules.append(max(far_ir(1,far_BC),near_ir(1,near_BC)))
        moves.append(0)
        turns.append(45)
    #R8 : front near then back
        rules.append((near_ir(0,near_BC)))
        moves.append(-10)
        turns.append(0) 

    #R9 : LINEAR FUZZY
        rules.append(max(far_ir(0,far_BC),near_ir(0,near_BC),mid_ir(0,mid_BC)))
        moves.append(4)
        turns.append(7) 
        print(max(far_ir(0,far_BC),near_ir(0,near_BC),mid_ir(0,mid_BC)))

        ans_turn = 0.0
        ans_move = 0.0
        for r, t, m in zip(rules, turns, moves):
            ans_turn += t * r
            ans_move += m * r

        self.turn(int(ans_turn))
        Move_update(int(ans_move))
        # Move_update(10)
        #Log()

if __name__ == '__main__':
   # app = PySimbotApp(map="no_wall",robot_cls=MyRobot, num_robots=1, interval=REFRESH_INTERVAL, enable_wasd_control=True)
    app = PySimbotApp(robot_cls=MyRobot, num_robots=1, interval=REFRESH_INTERVAL, enable_wasd_control=True)
    
    app.run()