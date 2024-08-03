from point import Point
from typing import List, Sequence, Tuple
import math
import pygame

def construct_random_chain(length):
    chain = []
    for i in range(length):
        chain.append((i*5,i*5))
    return chain



class Chain:
    def __init__(self, points:Sequence[Tuple[float, float]], link_length, color = "white") -> None:
        self.points = []
        for x, y in points:
            self.points.append(Point(x, y))
        self.points_number = len(self.points)
        self.first_point = self.points[0]
        self.last_point = self.points[-1]
        self.link_length = link_length
        self.color = pygame.Color(color)

    points:List[Point]

    def applyAccumulatedOffsets(self):
        for point in self.points:
            point.apply_accumulated_offset()
            
    #make pair iteration convenient:
    def __iter__(self):
        self.pair_index = 0
        return self

    def __next__(self):
        if self.pair_index < len(self.points) - 1:
            result = (self.points[self.pair_index], self.points[self.pair_index + 1])
            self.pair_index += 1
            return result
        else:
            raise StopIteration
    
    def get_co_tuples(self):
        l = []
        for p in self.points:
            l.append((p.co.x, p.co.y))
        return l
    
    def enforce_link_length(self, link_length = None):
        if not link_length:
            link_length = self.link_length
        for i in range(self.points_number-1):
            a = self.points[i]
            b = self.points[i+1]
            correction = b.co - a.co
            correction_amount = (correction.length() - link_length)
            if correction.length()>0.01:
                correction.scale_to_length(correction_amount)
            correction/=2
            a.add_offset(correction.x, correction.y)
            b.add_offset(-correction.x, -correction.y)
    
    def enforce_minimum_secondary_joint_distance(self, distance:float):
        hop_num = math.ceil( distance/self.link_length)
        for i in range(self.points_number-hop_num):
            a = self.points[i]
            b = self.points[i+hop_num]
            diff = b.co - a.co
            if diff.length_squared() < distance*distance:
                correction_amount = diff.length() - distance
                diff.scale_to_length(correction_amount/4)
                a.add_offset(diff.x, diff.y)
                b.add_offset(-diff.x, -diff.y)
    
    def add_point(self, point:Point, append_to_start:bool):
        if append_to_start:
            self.points.insert(0, point)
            self.first_point = point
        else:
            self.points.append(point)
            self.last_point = point
        self.points_number+=1
    
    

    
