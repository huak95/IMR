from kivy.uix.widget import WidgetBase
from typing import Sequence, Tuple, Optional, Union

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
        buttom_left = (widget.x, widget.y)
        buttom_right = (widget.x + widget.width, widget.y)
        top_left = (widget.x, widget.y + widget.height)
        top_right = (widget.x + widget.width, widget.y + widget.height)
        yield (buttom_left, buttom_right)
        yield (buttom_right, top_right)
        yield (top_right, top_left)
        yield (top_left, buttom_left)

    @staticmethod
    def line_segment_intersect(p1: Point2D, p2: Point2D, p3: Point2D, p4: Point2D) -> Union[None, Point2D]:
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
        return None

    @staticmethod
    def line_segment_circle_intersect(p1: Point2D, p2: Point2D, center: Point2D, radius: float) -> Tuple[Union[None, Point2D], Union[None, Point2D]]:
        x1, y1 = p1
        x2, y2 = p2
        xc, yc = center
        a = (x2-x1)**2 + (y2-y1)**2
        b = 2* ((x2-x1)*(x1-xc) + (y2-y1)*(y1-yc))
        c = (x1-xc)**2 + (y1-yc)**2 - radius**2
        discriminant = b**2 - 4*a*c
        if discriminant < 0:
            return (None, None)
        elif discriminant == 0:
            t = -b/(2*a)
            return ((x1+t*(x2-x1), y1+t*(y2-y1)), None)
        else:
            t1 = (-b - math.sqrt(discriminant)) / (2*a)
            t2 = (-b + math.sqrt(discriminant)) / (2*a)
            return ((x1+t1*(x2-x1), y1+t1*(y2-y1)), (x1+t2*(x2-x1), y1+t2*(y2-y1)))

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