from kivy.uix.widget import WidgetBase
from typing import Sequence, Tuple, Optional

import math

class Util:
    Point2D = Tuple[float, float] #x, y
    BBox = Tuple[float, float, float, float] #x, y, w, h

    @staticmethod
    def is_bbox_overlap(bbox1: BBox, bbox2: BBox) -> bool:
        if (bbox1[2] < bbox2[0]) or (bbox1[0] > bbox2[2]) or (bbox1[3] < bbox2[1]) or (bbox1[1] > bbox2[3]):
            return False
        return True

    @staticmethod
    def all_bounding_lines_generator(widgets: Sequence[WidgetBase]):
        for w in widgets:
            for x in Util.bounding_lines_generator(w):
                yield x

    @staticmethod
    def bounding_lines_generator(widget: WidgetBase):
        buttom_left = (widget.pos[0], widget.pos[1])
        buttom_right = (widget.pos[0] + widget.width, widget.pos[1])
        top_left = (widget.pos[0], widget.pos[1] + widget.height)
        top_right = (widget.pos[0] + widget.width, widget.pos[1] + widget.height)
        yield (buttom_left, buttom_right)
        yield (buttom_right, top_right)
        yield (top_right, top_left)
        yield (top_left, buttom_left)

    @staticmethod
    def line_segment_intersect(p1: Point2D, p2: Point2D, p3: Point2D, p4: Point2D) -> Point2D:
        # ref: http://www.cs.swan.ac.uk/~cssimon/line_intersection.html
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        x4, y4 = p4
        denominator = (x4 - x3) * (y1 - y2) - (x1 - x2) * (y4 - y3)
        # not parallel lines
        if denominator != 0:
            ta = ((y3 - y4) * (x1 - x3) + (x4 - x3) * (y1 - y3)) / denominator
            tb = ((y1 - y2) * (x1 - x3) + (x2 - x1) * (y1 - y3)) / denominator
            # segment has intersection
            if 0 <= ta <= 1 and 0 <= tb <= 1:
                return (x1 + ta*(x2-x1), y1 + ta*(y2-y1))

    @staticmethod
    def distance(p1: Point2D, p2: Point2D) -> float:
        return math.sqrt( (p1[0]-p2[0]) ** 2 + (p1[1]-p2[1]) ** 2 )

    @staticmethod
    def arange(start: float, stop: Optional[float]=None, step: Optional[float]=1.0):
        if stop is None:
            stop = start
            start = 0.0
        if step == 0:
            raise ValueError("arange() arg 3 must not be zero")
        i = 0
        total_round = round((stop - start) / step)
        while i < total_round:
            yield start + i * step
            i += 1