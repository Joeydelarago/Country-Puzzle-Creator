from typing import List, Tuple


class Polygon:
    def __init__(self, points: List[Tuple[int, int]], name=None):
        self.points: List[Tuple[int, int]] = points
        self.name = name

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
