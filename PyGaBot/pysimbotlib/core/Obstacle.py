#!/usr/bin/python3
from kivy.uix.widget import Widget
from kivy.logger import Logger
from typing import Sequence

class Obstacle(Widget):
    pass

class ObstacleWrapper(Widget):
    
    def get_obstacles(self) -> Sequence[Obstacle]:
        return [obstacle for obstacle in self.children if isinstance(obstacle, Obstacle)]