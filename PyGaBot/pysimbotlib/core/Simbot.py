#!/usr/bin/python3
import os, sys

from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, StringProperty
from kivy.logger import Logger
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout

import random

from .Obstacle import ObstacleWrapper
from .Objective import ObjectiveWrapper
from .Robot import RobotWrapper
from .config import SIMBOTMAP_SIZE

class Simbot(BoxLayout):
    
    _robots = ObjectProperty(None)
    _obstacles = ObjectProperty(None)
    _objectives = ObjectProperty(None)

    iteration = NumericProperty(0)
    max_tick = NumericProperty(0)
    simulation_count = NumericProperty(0)

    # stats
    eat_count = NumericProperty(0)
    food_move_count = NumericProperty(0)
    score = NumericProperty(0)
    scoreStr = StringProperty("")

    def __init__(self, 
                robot_cls, 
                num_robots, 
                robot_start_pos,
                customfn_create_robots = None, 
                customfn_before_simulation = None,
                customfn_after_simulation = None,
                simulation_forever = False,
                food_move_after_eat = True,
                **kwargs):
        super(Simbot, self).__init__(**kwargs)

        # initialize obstacles, objectives, and robot wrapper
        self._obstacles = ObstacleWrapper()
        self._objectives = ObjectiveWrapper()
        self._robots = RobotWrapper()
        self._robot_list = []

        # add robot to wrapper
        if customfn_create_robots:
            self.customfn_create_robots = customfn_create_robots
        else:
            self.robot_cls = robot_cls
            self.num_robots = num_robots    
        self.robot_start_pos = robot_start_pos

        # intialize simulation parameters
        self._before_simulation = customfn_before_simulation if customfn_before_simulation else lambda simbot: None
        self._after_simulation = customfn_after_simulation if customfn_after_simulation else lambda simbot: None
        self.simulation_forever = simulation_forever
        self.food_move_after_eat = food_move_after_eat
    
    @property
    def robots(self):
        return self._robot_list

    @property
    def obstacles(self):
        return self._obstacles.get_obstacles()

    @property
    def objectives(self):
        return self._objectives.get_objectives()

    def _create_robots(self):
        self._robot_list = self.customfn_create_robots() if hasattr(self, 'customfn_create_robots') else [self.robot_cls() for _ in range(self.num_robots)]
        for r in self._robot_list:
            r.pos = self.robot_start_pos
            r._sm = self
            self._robots.add_widget(r)

    def _remove_all_robots_from_map(self):
        self._robots.clear_widgets()
        self._robot_list.clear()

    def _reset_stats(self):
        self.eat_count = 0
        self.food_move_count = 0
        self.score = 0
        if self.food_move_after_eat:
            self.scoreStr = str(self.score) + " %"
        else:
            self.scoreStr = str(self.score)

    def process(self, dt):
        if self.iteration == 0:
            self._reset_stats()
            self._create_robots()
            self._before_simulation(self)
            self.simulation_count += 1
            Logger.debug('Map: Start Simulation')
            self.iteration += 1

        elif self.iteration <= self.max_tick:
            self.iteration += 1
            Logger.debug('Map: Start Iteration')
            for robot in self._robots.get_robots():
                robot.update()
            Logger.debug('Map: End Iteration: {}'.format(self.iteration))

            if self.iteration == self.max_tick:
                self._after_simulation(self)
                Logger.debug('Map: End Simulation: {}'.format(self.simulation_count))
                if self.simulation_forever:
                    self._remove_all_robots_from_map()
                    self.iteration = 0
    
    def on_robot_eat(self, robot, obj):
        self.eat_count += 1
        if self.food_move_after_eat:
            self.food_move_count += 1
            self.change_objective_pos(obj)
            self.score = int(self.eat_count * 100 / self.food_move_count)
            self.scoreStr = str(self.score) + " %"
        else:
            self.score += 5
            self.scoreStr = str(self.score)

    def change_objective_pos(self, obj, pos=None):
        if pos:
            obj.pos = pos
        else:
            new_pos = (random.randrange(SIMBOTMAP_SIZE[0]), random.randrange(SIMBOTMAP_SIZE[1]))
            while not self.is_objective_pos_valid(obj, new_pos):
                new_pos = (random.randrange(SIMBOTMAP_SIZE[0]), random.randrange(SIMBOTMAP_SIZE[1]))
            obj.pos = new_pos
            

    def is_objective_pos_valid(self, obj, pos):
        # check wall
        if pos[0] < 0 or pos[0] > SIMBOTMAP_SIZE[0] - obj.size[0]:
            return False
        if pos[1] < 0 or pos[1] > SIMBOTMAP_SIZE[1] - obj.size[1]:
            return False

        # check obstracles
        for obs in self.obstacles:
            if (obs.pos[0] < pos[0] < obs.pos[0] + obs.size[0] or obs.pos[0] < pos[0] + obj.size[0] < obs.pos[0] + obs.size[0])\
                and (obs.pos[1] < pos[1] < obs.pos[1] + obs.size[1] or obs.pos[1] < pos[1] + obj.size[1] < obs.pos[1] + obs.size[1]):
                return False
        return True

class PySimbotMap(Widget):
    def __init__(self,
                simbot,
                enable_wasd_control = False,
                **kwargs):
        super(PySimbotMap, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.enable_wasd_control = enable_wasd_control

        self.add_widget(simbot._obstacles)
        self.add_widget(simbot._objectives)
        self.add_widget(simbot._robots)
        
        self.simbot = simbot
        self.size = SIMBOTMAP_SIZE
    
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None
    
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if self.simbot.iteration >= self.simbot.max_tick:
            return
        if keycode[1] == 'n':
            for obj in self.simbot.objectives:
                self.simbot.change_objective_pos(obj)
                self.simbot.food_move_count += 1
                self.simbot.score = int(self.simbot.eat_count * 100 / self.simbot.food_move_count)
        elif keycode[1] == 'w' and self.enable_wasd_control:
            for r in self.simbot.robots:
                r.move(5)
        elif keycode[1] == 'a' and self.enable_wasd_control:
            for r in self.simbot.robots:
                r.turn(-5)
        elif keycode[1] == 'd' and self.enable_wasd_control:
            for r in self.simbot.robots:
                r.turn(5)
        elif keycode[1] == 's' and self.enable_wasd_control:
            for r in self.simbot.robots:
                r.move(-5)
        elif keycode[1] == 'q' and self.enable_wasd_control:
            for r in self.simbot.robots:
                r.turn(-5)
                r.move(5)
        elif keycode[1] == 'e' and self.enable_wasd_control:
            for r in self.simbot.robots:
                r.turn(5)
                r.move(5)