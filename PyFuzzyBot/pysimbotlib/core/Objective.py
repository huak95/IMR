#!/usr/bin/python3
from kivy.uix.widget import Widget
from kivy.logger import Logger
from typing import Sequence

class Objective(Widget):
    pass

class ObjectiveWrapper(Widget):

    def get_objectives(self) -> Sequence[Objective]:
        return [obj for obj in self.children if isinstance(obj, Objective)]