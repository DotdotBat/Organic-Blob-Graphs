from point import Point

from typing import List, Sequence, Tuple
import math
import pygame
from pygame.math import Vector2


class Chain:
    def __init__(self, color = None) -> None:
        self.points = []
        if color ==None:
            color = "white"
        self.color = pygame.Color(color)
    
    @property
    def point_start(self) -> Point:
        """First point"""
        return self.points[0]
    @point_start.setter
    def point_start(self, point:Point):
        self.points[0] = point

    @property
    def point_end(self) -> Point:
        """Last point"""
        return self.points[-1]
    
    @point_end.setter
    def point_end(self, point:Point):
        self.points[-1] = point

    @property
    def points_number(self) -> int:
        return len(self.points)

    points:List[Point]

    blob_left: 'Blob' = None # type: ignore
    blob_right:"Blob" = None # type: ignore


    @classmethod
    def from_point_list(cls, points:Sequence[Point], color = None) -> "Chain":
        chain = cls(color)
        chain.points = points[:] #list soft copy 
        return chain
    
    @classmethod
    def from_coord_list(cls, coords:Sequence[Tuple[float, float]], color = None) -> "Chain":
        points = []
        for x, y in coords:
            points.append(Point(x, y))
        chain = cls.from_point_list(points, color)
        return chain

    @classmethod
    def from_end_points(cls, start:Point, end:Point, link_length:float = None, color= None, point_num:int=None):
        """either point_num or link_length must be specified. Point_num takes precidence"""
        chain = cls()
        if color:
            chain.color = pygame.Color(color)
        
        chain.points.append(start)
        chain_length = start.co.distance_to(end.co)
        if not point_num:
            point_num = math.ceil(chain_length/link_length)
        for i in range(1, point_num-1):
            t = i/point_num
            inter = start.co.lerp(end.co, t)
            point = Point(inter.x, inter.y)
            chain.points.append(point)
        chain.points.append(end)
        return chain 

    def apply_accumulated_offsets(self, ignore_unmoving_status = False):
        if not ignore_unmoving_status:
            if self.is_unmoving:
                return
        for point in self.points:
            point.apply_accumulated_offset()



    #make pair iteration convenient:
    def __iter__(self):
        self._pair_index = 0
        return self

    def __next__(self):
        if self._pair_index < len(self.points) - 1:
            result = (self.points[self._pair_index], self.points[self._pair_index + 1])
            self._pair_index += 1
            return result
        else:
            raise StopIteration
    
    def get_co_tuples(self):
        l = []
        for p in self.points:
            l.append((p.co.x, p.co.y))
        return l
    
    def enforce_link_length(self, link_length:float, ignore_umoving_status = False):
        if not ignore_umoving_status:
            if self.is_unmoving:
                return
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
    
    def enforce_minimum_secondary_joint_distance(self, distance:float, link_length):
        if self.is_unmoving:
            return
        hop_num = math.ceil( distance/link_length)
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
        else:
            self.points.append(point)
    
    def common_endpoint(self, other:'Chain', raise_error_if_none = True):
        ss = self.point_start
        se = self.point_end
        os = other.point_start
        oe = other.point_end
        if ss == os or ss == oe:
            return ss
        if se == os or se == oe:
            return se
    
        if raise_error_if_none:
            raise ValueError("none of the endpoints are shared", self, other, ss, se, os, oe)

    def is_connected_to(self, other:'Chain'):
        if self.common_endpoint(other, raise_error_if_none=False):
            return True
        else:
            return False

    def set_blobs(self, right = None, left = None):
        if right:
            self.blob_right = right
        if left:
            self.blob_left = left

    @property
    def is_unmoving(self)->bool:
        if self.blob_left == None or self.blob_right == None:
            return True
        return self.blob_left.is_unmoving or self.blob_right.is_unmoving     
    
    def cut(self, point_index:int):
        if point_index <= 0 or point_index >= self.points_number - 1:
            raise ValueError("You are trying to cut too close to one of the ends of the chain. You are cutting at:", point_index, "While minimum is 1 and max is", self.points_number-2)

        start_points =  self.points[:point_index+1]
        end_points =    self.points[point_index:]
        self.points = start_points
        chain_start = self
        chain_end = Chain.from_point_list(points=end_points, color=self.color)
        chain_end.set_blobs(right=self.blob_right, left=self.blob_left)

        if not chain_start.is_connected_to(chain_end):
            raise RuntimeError()
        return chain_start, chain_end
    
    def __str__(self) -> str:
        return f'Chain from {self.point_start} to {self.point_end} with {self.points_number-2} in between'
    __repr__ = __str__

    def right_normal_at(self, point_index, normalize=False):
        i1 = max(0, point_index-1)
        i2 = min(point_index+1, self.points_number-1)
        p1 = self.points[i1]
        p2 = self.points[i2]
        diff = p2.co - p1.co
        #rotation to the right by a right angle example:
        # ( 1,-2) -> ( 2, 1)
        # ( 2, 1) -> (-1, 2)
        # ( x, y) -> (-y, x)

        rot = Vector2(-diff.y, diff.x)
        if(normalize):
            rot.normalize_ip()
        return rot

    def add_right_offset(self, offset_magnitude, ignore_umoving_status = False):
        if not ignore_umoving_status:
            if self.is_unmoving:
                return
        for i, p in enumerate(self.points):
            n = self.right_normal_at(i)
            n.scale_to_length(offset_magnitude)
            p.add_offset(n.x, n.y)    
    
    def get_on_blob_point_index(self, blob, chain_point_index):
        is_flipped = blob.is_chain_backwards(self)
        chain_index = blob.chain_loop.index(self)
        point_count = 0 
        for chain in blob.chain_loop:
            if chain == self:
                break
            point_count+= chain.points_number - 1
        
        if not is_flipped:
            blob_point_index = point_count + chain_point_index
        else:
            blob_point_index = point_count + chain.points_number - 1 - chain_point_index
        return blob_point_index    
        
    
