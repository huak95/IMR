#!/usr/bin/python3

from numpy.random import f, rand
from pysimbotlib.core import PySimbotApp, Simbot, Robot, Util
from kivy.logger import Logger
from kivy.config import Config
from pysimbotlib.core.config import SIMBOTMAP_SIZE
import os

from copy import deepcopy
import random
import csv
import os
import copy
import numpy as np

global angle_arr, n_robot, round_count, move_arr, step_arr, energy_arr, pose_arr,cumu_round_count, death_count
n_robot = 16

# Use positionarray to determine the robot is really stuck or not
# Use move and angle array to determine the robot have a good posture or not
angle_arr = [0]*n_robot
move_arr = [0]*n_robot
step_arr  = [0]*n_robot
energy_arr  = [0]*n_robot
pose_arr = [0]*n_robot
pos_arr = [0]*n_robot
round_count = n_robot - 1
cumu_round_count = 0
death_count = 0
print(angle_arr)


# # Force the program to show user's log only for "info" level or more. The info log will be disabled.
# Config.set('kivy', 'log_level', 'debug')
Config.set('graphics', 'maxfps', 300)

class StupidRobot(Robot):
    global angle_arr, n_robot, round_count, move_arr, step_arr, energy_arr, pose_arr, cumu_round_count, death_count

    RULE_LENGTH = 11
    NUM_RULES = 10

    def __init__(self, **kwarg):
        super(StupidRobot, self).__init__(**kwarg)
        self.RULES = [[0] * self.RULE_LENGTH for _ in range(self.NUM_RULES)]

        # initial list of rules
        self.rules = [0.] * self.NUM_RULES
        self.turns = [0.] * self.NUM_RULES
        self.moves = [0.] * self.NUM_RULES

        self.fitness = 0
        self.lazy_count = 0
        self.headache_count = 0
        self.energy = 300
        self.just_eat = False
        self.stuck = False
        self.roughmove_count = 0;         self.roughturn_count = 0
        self.roughturn2_count = 0;        self.roughturn3_count = 0
        self.walkback_count = 0;        self.walkforward_count = 0 
        self.twotask_count = 0;         self.circle_count = 0
        self.goodmove_count = 0;        self.pre_move = 0; self.static_count=0; 
        self.pre_pos=[0,0]; self.goodturn_count=0; self.greatturn_count=0
        self.diff_r=0; self.aim =0
    def update(self):
        ''' Update method which will be called each frame
        '''        
        self.ir_values = self.distance()
        self.S0, self.S1, self.S2, self.S3, self.S4, self.S5, self.S6, self.S7 = self.ir_values
        self.target = self.smell_nearest()
        if self.energy < 200 :
            self.set_color(0,0,255,0.2) # L BLUE
        elif self.energy < 500 :
            self.set_color(0,0,255,0.4) # BLUE       
        elif self.energy >= (np.sort(energy_arr))[-2] and self.energy < max(energy_arr):
            self.set_color(255,0,0,0.4) # L RED
        elif self.energy == max(energy_arr):
            self.set_color(255,0,0,1) # RED
        else:
            self.set_color(0,0,255,1) # BLUE
        if self.goodmove_count:
            self.set_color(0,255,0,1) # Green

        for i, RULE in enumerate(self.RULES):
            self.rules[i] = 1.0
            for k, RULE_VALUE in enumerate(RULE):
                if k < 8:
                    if RULE_VALUE % 5 == 1:
                        if k == 0: self.rules[i] *= self.S0_near()
                        elif k == 1: self.rules[i] *= self.S1_near()
                        elif k == 2: self.rules[i] *= self.S2_near()
                        elif k == 3: self.rules[i] *= self.S3_near()
                        elif k == 4: self.rules[i] *= self.S4_near()
                        elif k == 5: self.rules[i] *= self.S5_near()
                        elif k == 6: self.rules[i] *= self.S6_near()
                        elif k == 7: self.rules[i] *= self.S7_near()
                    elif RULE_VALUE % 5 == 2:
                        if k == 0: self.rules[i] *= self.S0_far()
                        elif k == 1: self.rules[i] *= self.S1_far()
                        elif k == 2: self.rules[i] *= self.S2_far()
                        elif k == 3: self.rules[i] *= self.S3_far()
                        elif k == 4: self.rules[i] *= self.S4_far()
                        elif k == 5: self.rules[i] *= self.S5_far()
                        elif k == 6: self.rules[i] *= self.S6_far()
                        elif k == 7: self.rules[i] *= self.S7_far()
                elif k == 8:
                    temp_val = RULE_VALUE % 6
                    if temp_val == 1: self.rules[i] *= self.smell_left()
                    elif temp_val == 2: self.rules[i] *= self.smell_center()
                    elif temp_val == 3: self.rules[i] *= self.smell_right()
                elif k==9: self.turns[i] = (((RULE_VALUE) % 181) - 90); 
                elif k==10: self.moves[i] = (RULE_VALUE % 21) - 5; # print(f'self.moves[i]: {self.moves[i]}')
        
        answerTurn = 0.0
        answerMove = 0.0

        for turn, move, rule in zip(self.turns, self.moves, self.rules):
            answerTurn += turn * rule
            answerMove += move * rule
        
        global round_count, cumu_round_count, death_count
        self.pre_move = move_arr[round_count]
        # _______________Count Command______________

        if round_count == (n_robot-1):
            round_count = 0
            cumu_round_count += 1
            # print("Next Iteration")
            # print(f"step: {(step_arr)}")
            # print(f"move: {(move_arr)}")
            # print(f"pose: {pose_arr}")
            # print(f"angle: {(angle_arr)}")
            # print(f"energy: {energy_arr}")
            if cumu_round_count % 2000 == 0:
                f = open("death_count.csv","a")
                f.write(f"{cumu_round_count}, {death_count}\n")
                death_count = 0
            
        else:
            round_count += 1 

        angle_arr[round_count] += int(answerTurn)
        move_arr[round_count] += int(answerMove+1)

        self.pre_pos = np.array(self.pos)
        step_arr[round_count] += 1

        self.th_c = 4 # Treshold
        treshold1 = step_arr[round_count] > self.th_c
        treshold2 = step_arr[round_count] > self.th_c 

        condi1 = (move_arr[round_count] < 50 )
        
        if abs(angle_arr[round_count]) >= 360 and condi1 and treshold2 :
            self.circle_count = 1
            angle_arr[round_count] = 0
            move_arr[round_count] = 0
        else: self.circle_count = 0

        if abs(int(answerTurn)) > 30:
            self.headache_count = 1
        else: self.headache_count = 0

        if int(answerMove) < 5:
            self.roughmove_count = 1
        else: self.roughmove_count = 0

        diff_food2 = abs(int(answerTurn-self.smell_nearest()))

        if (abs(int(answerTurn)) > 15) and diff_food2 >= 30:
            self.roughturn_count = 1
        else: self.roughturn_count=0

        if (abs(int(answerTurn)) < 20) and diff_food2 < 15 and int(answerMove) > 5:
            self.goodturn_count = 1
        else: self.goodturn_count=0

        if (abs(int(answerTurn)) < 10) and diff_food2 < 10 and int(answerMove) > 5:
            self.greatturn_count = 1
        else: self.greatturn_count=0

        if (round(answerMove) < 0 ) :
            self.walkback_count = 1
        else: self.walkback_count=0

        # _______________Move Command______________
        self.turn(int(answerTurn))
        self.move((int(answerMove)))

        diff = (np.array(self.pre_pos) - np.array(self.pos))
        self.diff_r = round(np.sqrt(diff[0]**2 + diff[1]**2))
        if self.diff_r <= 1:
            self.static_count = 1
        else:
            self.static_count = 0

        # Aim for food
        diff_food3 = abs(int(answerTurn-self.smell_nearest()))
        aim = abs(int(self.smell_center()*10))
        if move_arr[round_count] > 100 and abs(int(answerMove)) >= 2 and treshold1 and diff_food3 < 10 and aim < 10 and self.diff_r >= 3:
            self.goodmove_count = 1
        else: self.goodmove_count = 0
            
        if self.diff_r < 3 and abs(int(answerMove)) <= 2 and treshold1:
            self.lazy_count = 1
        else: self.lazy_count = 0

        if (int(answerMove) > 0 and self.diff_r > 2):
            self.walkforward_count = 1
        else: self.walkforward_count = 0

        
        # _______________Energy Command______________

        if self.circle_count:
            self.energy -= 200
            self.pose_count -= 20
            pass

        # # if the robot turn around, it  lost energy
        if self.headache_count :
            self.energy -= 200
            self.pose_count -= 5
            pass    

        # # if the have a good move, it  gain energy
        if self.goodmove_count:
            self.energy +=50
            self.pose_count += 10
            pass

        # if the robot eat food, it gets some energy back
        if self.just_eat :
            self.energy += 400
            pass

        # if the static struck, it also lost energy
        if self.static_count:
            self.energy -= 3
            pass

        # if the robot hit and static, it also lost energy
        if self.just_hit and self.static_count:
            self.energy -= 3
            pass        
        
        # # if the robot Lazy, it  lost energy
        if self.lazy_count :
            self.energy -= 5
            pass        

        if self.walkback_count :
            self.energy -= 3
            pass     

        if self.walkforward_count :
            self.energy += 10
            self.pose_count += 10
            pass     
        
        energy_arr[round_count] = int(self.energy)
        pose_arr[round_count] = self.pose_count
        
        def init_arr():
            angle_arr[round_count] = 0 ; move_arr[round_count] = 0; step_arr[round_count]=0; energy_arr[round_count]=0 ; pose_arr[round_count]=0; self.eat_count = 0
            self.pose_count = 0

        if self.energy < 0 :
            init_arr()
            death_count += 1
            temp = self.generate_new_robot()
            self.RULES = deepcopy(temp.RULES)
            # Obtain the new position from temp Robot
            self.pos = temp.pos
            self.energy = 500
            pass
        
# _____________________________________generate_new_robot_______________________________________________________
    def generate_new_robot(self):
        simbot = self._sm
        num_robots = len(simbot.robots)
        simbot.robots_energy.sort(key=lambda robot: robot.energy, reverse=True)
        simbot.robots_fitness.sort(key=lambda robot: robot.eat_count, reverse=True)

        def Change_New_Pos(StupidRobot) ->StupidRobot:
            temp = StupidRobot
            # Change New position
            temp.pos = (random.randrange(SIMBOTMAP_SIZE[0] - temp.size[0]), random.randrange(SIMBOTMAP_SIZE[1] - temp.size[1]))
            trial_count = 0
            # Checking position of all robots with new position
            while not simbot.is_robot_pos_valid(temp):
                # Random New Location
                temp.pos = (random.randrange(SIMBOTMAP_SIZE[0] - temp.size[0]), random.randrange(SIMBOTMAP_SIZE[1] - temp.size[1]))
                trial_count += 1
                if trial_count == 500:
                    raise Exception("Can't find the place for spawning robots")
            return temp

        def select_best_score() -> StupidRobot:
            index = random.randrange(0,4)
            return simbot.robots_fitness[index] 

        def select_best_energy() -> StupidRobot:
            index = random.randrange(0,4)
            # print(f'simbot.robots_energy: {simbot.robots_energy}')
            return simbot.robots_energy[index]

        father = select_best_energy()

        mother = select_best_score()   # design the way for selection by yourself

        while father == mother:
            mother = select_best_score()
            
        son = StupidRobot()
        #_______________________________________________________________________________________________
        # Doing crossover
        #     using next_gen_robots for temporary keep the offsprings, later they will be copy
        #     to the robots

        # First Cross
        chromosome = random.randint(0,9)
        # genevalue = random.randint(3,7)
        genevalue = random.randint(0,10)
        son.RULES[:chromosome] = copy.deepcopy(father.RULES[:chromosome])
        son.RULES[chromosome][:genevalue] = copy.deepcopy(father.RULES[chromosome][:genevalue])
        son.RULES[chromosome][genevalue:] = copy.deepcopy(mother.RULES[chromosome][genevalue:])
        son.RULES[chromosome+1:] = copy.deepcopy(mother.RULES[chromosome + 1:])
    
        # Doing mutation
        #     generally scan for all next_gen_robots we have created, and with very low
        #     propability, change one byte to a new random value.
        
        if random.randrange(0, 100) > 97: # mutation = 3 %
            i = random.randint(0,9)
            j = random.randint(0,10)
            son.RULES[i][j] = random.randint(0, 255)

        
        # If you wanna change the position after dea1 
        # you can call this "Change_New_Pos" function, 
        # If not, please comment this.
        Change_New_Pos(son)

        return son

    def S0_near(self):
        if self.S0 <= 0: return 1.0
        elif self.S0 >= 100: return 0.0
        else: return 1 - (self.S0 / 100.0)

    def S0_far(self):
        if self.S0 <= 0: return 0.0
        elif self.S0 >= 100: return 1.0
        else: return self.S0 / 100.0
    
    def S1_near(self):
        if self.S1 <= 0: return 1.0
        elif self.S1 >= 100: return 0.0
        else: return 1 - (self.S1 / 100.0)
    
    def S1_far(self):
        if self.S1 <= 0: return 0.0
        elif self.S1 >= 100: return 1.0
        else: return self.S1 / 100.0
    
    def S2_near(self):
        if self.S2 <= 0: return 1.0
        elif self.S2 >= 100: return 0.0
        else: return 1 - (self.S2 / 100.0)
    
    def S2_far(self):
        if self.S2 <= 0: return 0.0
        elif self.S2 >= 100: return 1.0
        else: return self.S2 / 100.0
    
    def S3_near(self):
        if self.S3 <= 0: return 1.0
        elif self.S3 >= 100: return 0.0
        else: return 1 - (self.S3 / 100.0)
    
    def S3_far(self):
        if self.S3 <= 0: return 0.0
        elif self.S3 >= 100: return 1.0
        else: return self.S3 / 100.0
    
    def S4_near(self):
        if self.S4 <= 0: return 1.0
        elif self.S4 >= 100: return 0.0
        else: return 1 - (self.S4 / 100.0)
    
    def S4_far(self):
        if self.S4 <= 0: return 0.0
        elif self.S4 >= 100: return 1.0
        else: return self.S4 / 100.0
    
    def S5_near(self):
        if self.S5 <= 0: return 1.0
        elif self.S5 >= 100: return 0.0
        else: return 1 - (self.S5 / 100.0)
    
    def S5_far(self):
        if self.S5 <= 0: return 0.0
        elif self.S5 >= 100: return 1.0
        else: return self.S5 / 100.0
    
    def S6_near(self):
        if self.S6 <= 0: return 1.0
        elif self.S6 >= 100: return 0.0
        else: return 1 - (self.S6 / 100.0)
    
    def S6_far(self):
        if self.S6 <= 0: return 0.0
        elif self.S6 >= 100: return 1.0
        else: return self.S6 / 100.0
    
    def S7_near(self):
        if self.S7 <= 0: return 1.0
        elif self.S7 >= 100: return 0.0
        else: return 1 - (self.S7 / 100.0)
    
    def S7_far(self):
        if self.S7 <= 0: return 0.0
        elif self.S7 >= 100: return 1.0
        else: return self.S7 / 100.0
    
    def smell_right(self):
        if self.target >= 45: return 1.0
        elif self.target <= 0: return 0.0
        else: return self.target / 45.0
    
    def smell_left(self):
        if self.target <= -45: return 1.0
        elif self.target >= 0: return 0.0
        else: return 1-(-1*self.target)/45.0
    
    def smell_center(self):
        if self.target <= 45 and self.target >= 0: return self.target / 45.0
        if self.target <= -45 and self.target <= 0: return 1-(-1*self.target)/45.0
        else: return 0.0

def write_rule(robot, filename):
    with open(filename, "a") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerows(robot.RULES)


def before_simulation(simbot: Simbot):
    f = open("death_count.csv","w")
    f.write(f"Iteration, Dead\n")
    f.closed
    for robot in simbot.robots:
        # random RULES value for the first generation
        if simbot.simulation_count == 0:
            Logger.info("GA: initial population")
            for i, RULE in enumerate(robot.RULES):
                for k in range(len(RULE)):
                    robot.RULES[i][k] = random.randrange(256)

def after_simulation(simbot: Simbot):
    for robot in simbot.robots:
        robot.fitness = robot.energy
    # descending sort and rank: the best 10 will be on the list at index 0 to 9
    simbot.robots.sort(key=lambda robot: robot.fitness, reverse=True)
    write_rule(simbot.robots[0], "best_robot_energy.csv")


if __name__ == '__main__':

    app = PySimbotApp(robot_cls=StupidRobot, 
                        num_robots=n_robot,
                        num_objectives=4,
                        theme='default',
                        simulation_forever=False,
                        max_tick=100000,
                        interval=1/300.0,
                        food_move_after_eat=True,
                        robot_see_each_other=True,
                        enable_wasd_control = True,
                        # map="no_wall",
                        customfn_before_simulation=before_simulation, 
                        customfn_after_simulation=after_simulation)
    app.run()