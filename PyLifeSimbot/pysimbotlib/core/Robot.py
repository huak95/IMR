#!/usr/bin/python3

import os, sys
import math
import random

from itertools import chain

from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.logger import Logger
from typing import Sequence, Tuple
from .Objective import Objective
from .Util import Util
from .config import SIMBOTMAP_SIZE, SIMBOTMAP_BBOX , ROBOT_DISTANCE_ANGLES, ROBOT_MAX_SENSOR_DISTANCE

class Robot(Widget):

    # Facing 0 degree direction
    _sm = None
    _direction = NumericProperty(0)
    
    _color_r = NumericProperty(0)
    _color_g = NumericProperty(0)
    _color_b = NumericProperty(0)
    _color_a = NumericProperty(0)

    color = ReferenceListProperty(_color_r, _color_g, _color_b, _color_a)
    
    eat_count: int = 0
    collision_count: int = 0
    pose_count: int = 0
    just_eat: bool = False
    just_hit: bool = False

    #Modified
    backward_count: int = 0
    turning_count: int = 0
    unwantmove_count: int = 0

    def _isValidPosition(self, p: Util.Point2D, obstacles_included=None) -> bool:
        if obstacles_included is None:
            obstacles_included = self._sm.obstacles
        # Check for outside wall
        if p[0] <= 0 or p[0] >= SIMBOTMAP_SIZE[0] or p[1] <= 0 or p[1] >= SIMBOTMAP_SIZE[1]:
            return False
        # Check obstacles
        for obs in obstacles_included:
            if p[0] <= obs.x or p[0] >= obs.x + obs.width or p[1] <= obs.y or p[1] >= obs.y + obs.height:
                continue
            return False

        # Check robots
        if self._sm.robot_see_each_other:
            for r in self._sm._robot_list:
                if r == self:
                    continue
                if Util.distance(r.center, p) <= 0.5 * self.size[0]:
                    return False

        return True

    @staticmethod
    def distance_to_line_generators(surf: Util.Point2D, outside_bot: Util.Point2D, bounding_lines):
        # overlapping_bounding_lines = obstacle_bounding_lines
        for line in bounding_lines:
            intersection = Util.line_segment_intersect(surf, outside_bot, line[0], line[1])
            yield (Util.distance(surf, intersection) if intersection else ROBOT_MAX_SENSOR_DISTANCE)

    @staticmethod
    def distance_to_robot_generators(surf: Util.Point2D, outside_bot: Util.Point2D, robots):
        for r in robots:
            intersection = Util.line_segment_circle_intersect(surf, outside_bot, r.center, r.width / 2)
            near_intersection = intersection[0]
            yield (Util.distance(surf, near_intersection) if near_intersection else ROBOT_MAX_SENSOR_DISTANCE)
        yield ROBOT_MAX_SENSOR_DISTANCE

    def _distance(self, angle: float) -> float:
        rad_angle = math.radians(-(self._direction+angle) % 360)
        unit_x = math.cos(rad_angle)
        unit_y = math.sin(rad_angle)

        # surf = (self.center_x + self.width / 2.0 * unit_x, self.center_y + self.height / 2.0 * unit_y)
        # ROI = ( min(surf[0], surf[0] + ROBOT_MAX_SENSOR_DISTANCE * unit_x),
        #         min(surf[1], surf[1] + ROBOT_MAX_SENSOR_DISTANCE * unit_y),
        #         max(surf[0], surf[0] + ROBOT_MAX_SENSOR_DISTANCE * unit_x),
        #         max(surf[1], surf[1] + ROBOT_MAX_SENSOR_DISTANCE * unit_y) )
        # outside_bot = (surf[0] + unit_x * ROBOT_MAX_SENSOR_DISTANCE, 
        #                 surf[1] + unit_y * ROBOT_MAX_SENSOR_DISTANCE)
        # obstacles_in_ROI = filter(lambda obs: Util.is_bbox_overlap(ROI, (obs.x, obs.y, obs.x + obs.width, obs.y + obs.height)), self._sm.obstacles)
        # obstacle_bounding_lines = Util.all_bounding_lines_generator(obstacles_in_ROI)
        # walls_bounding_lines = Util.all_bounding_lines_generator((self._sm, ))
        # overlapping_bounding_lines = filter(lambda obs: Util.is_bbox_overlap(ROI, (obs[0][0], obs[0][1], obs[1][0], obs[1][1])), obstacle_bounding_lines)
        # return min(Robot.distance_to_line_generators(surf, outside_bot, chain(walls_bounding_lines, overlapping_bounding_lines)))

        surf = (self.center_x + self.width / 2.0 * unit_x, 
                self.center_y + self.height / 2.0 * unit_y)
        ROI = ( min(surf[0], surf[0] + ROBOT_MAX_SENSOR_DISTANCE * unit_x),
                min(surf[1], surf[1] + ROBOT_MAX_SENSOR_DISTANCE * unit_y),
                max(surf[0], surf[0] + ROBOT_MAX_SENSOR_DISTANCE * unit_x),
                max(surf[1], surf[1] + ROBOT_MAX_SENSOR_DISTANCE * unit_y) )
        outside_bot = (surf[0] + unit_x * ROBOT_MAX_SENSOR_DISTANCE, surf[1] + unit_y * ROBOT_MAX_SENSOR_DISTANCE)
        obstacles_in_ROI = filter(lambda obs: Util.is_bbox_overlap(ROI, (obs.x, obs.y, obs.x + obs.width, obs.y + obs.height)), self._sm.obstacles)
        obstacle_bounding_lines = Util.all_bounding_lines_generator(obstacles_in_ROI)
        min_distance_to_wall_and_obs = min(Robot.distance_to_line_generators(surf, outside_bot, chain(SIMBOTMAP_BBOX, obstacle_bounding_lines)))
        
        if self._sm.robot_see_each_other:
            other_robots_in_ROI = filter(lambda r: r != self and Util.is_bbox_overlap(ROI, (r.x, r.y, r.x + r.width, r.y + r.height)), self._sm._robot_list)
            min_distance_to_other_robot = min(Robot.distance_to_robot_generators(surf, outside_bot, other_robots_in_ROI))
            return min(min_distance_to_wall_and_obs, min_distance_to_other_robot)
        else:
            return min_distance_to_wall_and_obs
        
        # surf = (self.center_x + self.width / 2.0 * unit_x, self.center_y + self.height / 2.0 * unit_y)
        # ROI = ( min(surf[0], surf[0] + ROBOT_MAX_SENSOR_DISTANCE * unit_x),
        #         min(surf[1], surf[1] + ROBOT_MAX_SENSOR_DISTANCE * unit_y),
        #         max(surf[0], surf[0] + ROBOT_MAX_SENSOR_DISTANCE * unit_x),
        #         max(surf[1], surf[1] + ROBOT_MAX_SENSOR_DISTANCE * unit_y) )
        # obstacles_in_ROI = list(filter(lambda obs: Util.is_bbox_overlap(ROI, (obs.x, obs.y, obs.x + obs.width, obs.y + obs.height)), self._sm.obstacles))
        # for i in range(0, ROBOT_MAX_SENSOR_DISTANCE + 1):
        #     new_i = (surf[0] + i * unit_x, surf[1] + i * unit_y)
        #     if self._isValidPosition(new_i, obstacles_in_ROI):
        #         continue
        #     return i
        # return ROBOT_MAX_SENSOR_DISTANCE

    def _isValidMove(self, next_position: Util.Point2D) -> bool:
        for angle in range(0, 360, 40):
            rad_angle = math.radians(-(self._direction+angle) % 360)
            unit_x = math.cos(rad_angle)
            unit_y = math.sin(rad_angle)
            surf = (next_position[0] + self.width / 2.0 * (unit_x+1), next_position[1] + self.height/2.0 * (unit_y+1))
            if not self._isValidPosition(surf):
                return False
        return True

    def _get_overlap_objective(self) -> Objective:
        for obj in self._sm.objectives:
            if (self.pos[0] < obj.x and self.pos[0] + self.width < obj.x) or \
                (self.pos[0] > obj.x + obj.width and self.pos[0] + self.width > obj.x + obj.width) or \
                (self.pos[1] < obj.y and self.pos[1] + self.height < obj.y) or \
                (self.pos[1] > obj.y + obj.height and self.pos[1] + self.height > obj.y + obj.height):
                continue
            return obj
        return None
        
    def set_color(self, r: float, g: float, b: float, a: float=1) -> None:
        self._color_r = r
        self._color_g = g
        self._color_b = b
        self._color_a = a

    def distance(self) -> Sequence[float]:
        return tuple(self._distance(angle) for angle in ROBOT_DISTANCE_ANGLES)
    
    def smell(self, index: int = 0) -> float:
        if index >= 0 and index < len(self._sm.objectives):
            # Get angle
            obj = self._sm.objectives[index]
            dvx = self.center_x - obj.center_x
            dvy = self.center_y - obj.center_y
            rad = math.atan2(dvy, dvx)
            deg = ((180 - (math.degrees(rad) + self._direction)) % 360)
            if(deg <= 180):
                return deg
            else:
                return deg - 360
        return 0

    def smell_nearest(self) -> float:
        nearest_food = min(self._sm.objectives, key=lambda food: Util.distance(self.pos, food.pos))
        obj = nearest_food
        dvx = self.center_x - obj.center_x
        dvy = self.center_y - obj.center_y
        rad = math.atan2(dvy, dvx)
        deg = ((180 - (math.degrees(rad) + self._direction)) % 360)
        if(deg <= 180):
            return deg
        else:
            return deg - 360

    def turn(self, degree: float = 1) -> None:
        self._direction = (self._direction + degree) % 360

    #Modified
    def turn_ref(self, degree: float = 1, ref: float = 1) -> None:
        if (int(self._direction) == int(ref)): #Already Inline with Ref
            self.turning_count -= 1
        self._direction = (self._direction + degree) % 360
        if (degree > 15 or degree < -15) and not(int(self._direction) == int(ref)):
            self.turning_count += 1
            if (self._direction-ref< 15 and self._direction-ref > -15) :
                self.turning_count -= 1

    def move(self, step: int = 1) -> None:
        rad_angle = math.radians((-self._direction) % 360)
        if step >= 0:
            step = int(step)
            #Modified
            if step < 7 or step>10:
                self.unwantmove_count +=1
            #---------
        else:
            rad_angle = math.radians((180-self._direction) % 360)
            step = int(-step)
            self.backward_count +=1

        dx = math.cos(rad_angle)
        dy = math.sin(rad_angle)

        self.just_hit = False

        next_position = self.pos
        for _ in range(0, step, 1):
            next_possible_position = (next_position[0] + dx, next_position[1] + dy)
            # If can move
            if not self._isValidMove(next_possible_position):
                self.collision_count += 1
                self.just_hit = True
                break
            next_position = next_possible_position
        self.pos = next_position

        obj = self._get_overlap_objective()
        if not obj:
            self.just_eat = False
        elif obj and not self.just_eat:
            Logger.debug('Robot: Eat Objective at [{}, {}]'.format(obj.pos[0], obj.pos[1]))
            self._sm.on_robot_eat(self, obj)
            self.eat_count += 1
            self.just_eat = True
        
    def update(self):
        pass

class RobotWrapper(Widget):
    def get_robots(self) -> Sequence[Robot]:
        return [robot for robot in self.children if isinstance(robot, Robot)]