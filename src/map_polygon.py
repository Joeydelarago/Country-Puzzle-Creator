import itertools
import logging
from typing import List, Tuple, Dict, Type


class MapPolygon:
    def __init__(self, points: List[Tuple[int, int]], name=None):
        self.borders = {}
        self.points = points
        self.name = name

        self.logger = logging.getLogger('map_polygon')
        logging.basicConfig()

    @property
    def points(self) -> List[Tuple[int, int]]:
        return self.__points

    @points.setter
    def points(self, p) -> None:
        self.__points = p

    @property
    def borders(self) -> Dict[Type["MapPolygon"], List[Tuple]]:
        """ A list of borders that overlap with other polygons"""
        return self.__borders

    @borders.setter
    def borders(self, b) -> None:
        self.__borders = b

    def outside_borders(self):
        """ Return a sorted flattened list of slices of all areas not bordering another polygon """
        outside_borders = []
        flattened_borders = self.flattened_borders()
        for i in range(len(flattened_borders)):
            outside_borders.append((flattened_borders[i-1][1], flattened_borders[i][0]))
        return outside_borders


    def flattened_borders(self):
        """ Return a sorted flattened list of all border slices"""
        return sorted(list(itertools.chain(*self.__borders.values())), key=lambda b: b[0])

    def extend_borders(self, borders, polygon: Type["MapPolygon"]):
        borders = sorted(borders, key=lambda b: b[0])
        self.__borders[polygon] = borders

        for i in range(1, len(borders)):
            if borders[i][0] < borders[i-1][1]:
                self.logger.warning(f"Borders between {polygon.name} and {self.name}, {borders[i][0]} and {borders[i-1][1]} are overlapping")

    def clear_borders(self):
        """ Clear this polygon from all other polygons border lists. Clear this polygons border list. """
        for poly in self.borders.keys():
            del poly.borders[self]

        self.borders = {}

    def min_x(self):
        return min(list(map(lambda p: p[0], self.points)))

    def min_y(self):
        return min(list(map(lambda p: p[1], self.points)))

    def max_x(self):
        return max(list(map(lambda p: p[0], self.points)))

    def max_y(self):
        return max(list(map(lambda p: p[1], self.points)))

    def __len__(self):
        return len(self.points)

    def __getitem__(self, index):
        return self.points[index]

    def __setitem__(self, key, value):
        self.points[key] = value
