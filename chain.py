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
    def point_start(self) -> "Point":
        """First point"""
        if self.point_number==0:
            return None
        return self.points[0]
    @point_start.setter
    def point_start(self, point:"Point"):
        self.points[0] = point

    @property
    def point_end(self) -> "Point":
        """Last point"""
        if self.point_number==0:
            return None
        return self.points[-1]
    
    @point_end.setter
    def point_end(self, point:"Point"):
        self.points[-1] = point

    @property
    def point_number(self) -> int:
        return len(self.points)

    points:List["Point"]

    blob_left = None 
    blob_right= None


    @classmethod
    def from_point_list(cls, points:Sequence["Point"], color = None) -> "Chain":
        chain = cls(color)
        chain.points = points[:] #list soft copy 
        for point in points:
            point.chains.add(chain)
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
        points = []
        points.append(start)
        chain_length = start.co.distance_to(end.co)
        if not point_num:
            point_num = math.ceil(chain_length/link_length)
        for i in range(1, point_num-1):
            t = i/point_num
            inter = start.co.lerp(end.co, t)
            point = Point(inter.x, inter.y)
            points.append(point)
        points.append(end)
        chain = cls.from_point_list(points, color)
        return chain 

    def apply_accumulated_offsets(self, ignore_unmoving_status = False):
        if not ignore_unmoving_status:
            if self.is_unmoving:
                return
        for point in self.points:
            point.apply_accumulated_offset(ignore_unmoving=ignore_unmoving_status)



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
        for i in range(self.point_number-1):
            a = self.points[i]
            b = self.points[i+1]
            correction = b.co - a.co
            correction_amount = (correction.length() - link_length)
            if correction.length()>0.01:
                correction.scale_to_length(correction_amount/2)
            a.add_offset(correction.x, correction.y)
            b.add_offset(-correction.x, -correction.y)
    
    def enforce_minimum_secondary_joint_distance(self, distance:float, link_length):
        if self.is_unmoving:
            return
        hop_num = math.ceil( distance/link_length)
        for i in range(self.point_number-hop_num):
            a = self.points[i]
            b = self.points[i+hop_num]
            diff = b.co - a.co
            if diff.length_squared() < distance*distance:
                correction_amount = diff.length() - distance
                diff.scale_to_length(correction_amount/4)
                a.add_offset(diff.x, diff.y)
                b.add_offset(-diff.x, -diff.y)
    
    def append_endpoint(self, point:Point, append_to_start:bool):
        point.chains.add(self)
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
        if self.is_unmoving_override is not None:
            return self.is_unmoving_override
        if self.blob_left is None or self.blob_right is None:
            return True
        return self.blob_left.is_unmoving_override or self.blob_right.is_unmoving_override    
    
    def cut(self, point_index:int):
        if point_index <= 0 or point_index >= self.point_number - 1:
            raise ValueError("You are trying to cut too close to one of the ends of the chain. You are cutting at:", point_index, "While minimum is 1 and max is", self.point_number-2)
        for point in self.points:
            point.chains.discard(self)

        start_points =  self.points[:point_index+1]
        for point in start_points:
            point.chains.add(self)
        end_points =    self.points[point_index:]

        self.points = start_points
        chain_start = self
        
        chain_end = Chain.from_point_list(points=end_points, color=self.color)
        chain_end.set_blobs(right=self.blob_right, left=self.blob_left)

        if not chain_start.is_connected_to(chain_end):
            raise RuntimeError()
        
        return chain_start, chain_end
    
    def __str__(self) -> str:
        named = ""
        if self.name is not None:
            named = self.name+" "
        if self.point_number==1:
            return f'a short {named}Chain only one {self.point_start}'
        if self.point_number == 0:
            return f'empty {named}Chain object'
        return f'{named}Chain from {self.point_start} to {self.point_end} with {self.point_number-2} in between'
    def __repr__(self):
        obj_id = id(self)
        hex_addr = hex(obj_id)[2:]  # Remove '0x' prefix
        return f"<{str(self)} at 0x{hex_addr}>"

    def right_normal_at(self, point_index, normalize=False):
        i1 = max(0, point_index-1)
        i2 = min(point_index+1, self.point_number-1)
        p1 = self.points[i1]
        p2 = self.points[i2]
        diff = p2.co - p1.co

        #examples of rotation to the right by a right angle:
        # ( 1,-2) -> ( 2, 1)
        # ( 2, 1) -> (-1, 2)
        #so in our coordinate system
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
            if (p == self.point_start or p == self.point_end):
                if p.is_unmoving and not ignore_umoving_status:
                    continue
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
            point_count+= chain.point_number - 1
        
        if not is_flipped:
            blob_point_index = point_count + chain_point_index
        else:
            blob_point_index = point_count + chain.point_number - 1 - chain_point_index
        return blob_point_index    
    
    def create_midpoint(self, point_index:int, next_index:int):
        if abs(point_index - next_index)!=1:
            raise RuntimeError("those are not neighbors")
        if point_index > next_index:
            point_index, next_index = next_index, point_index
        point = self.points[point_index]
        next_point = self.points[next_index]
        mid_co = (point.co + next_point.co)/2
        midpoint = Point(mid_co.x, mid_co.y)
        midpoint.chains.add(self)
        mid_offset = (point.offset + next_point.offset)/2
        midpoint.offset = mid_offset
        self.points.insert(point_index+1, midpoint)
        return midpoint
    
    def remove_point(self, point:int|Point):
        if type(point) == int:
            point_index = point
            point = self.points.pop(point_index)
        else:
            point:Point
            self.points.remove(point)
        point.chains.remove(self)
        return point
    
    def swap_point(self, point_to_remove:Point, point_to_insert:Point):
        point_index = self.points.index(point_to_remove)
        point_to_remove.chains.remove(self)
        point_to_insert.chains.add(self)
        self.points[point_index] = point_to_insert
    
    def unregister_from_blobs(self):
        # pass
        if self.blob_left is not None:
            self.blob_left.chain_loop.remove(self)
            self.blob_left = None
        if self.blob_right is not None:
            self.blob_right.chain_loop.remove(self)
            self.blob_right = None
    
    def close(self):
        if self.point_start != self.point_end:
            self.points.append(self.point_start)
    
    is_unmoving_override:bool = None

    def find_biggest_gap(self)->tuple [int, int, float]:
        if self.point_number<2:
            raise ValueError("Trying to find the biggest gap on a chain too short to have any gaps")
        best_so_far = (-1, -1, 0)
        for i in range(self.point_number - 1):
            next_i = i+1
            p, next_p = self.points[i], self.points[next_i]
            gap_length = p.co.distance_to(next_p.co)
            _, _, biggest_gap_so_far = best_so_far
            if gap_length > biggest_gap_so_far:
                best_so_far = i, next_i, gap_length
        return best_so_far
    
    def endpoint_neighbor(self, endpoint:Point):
        if self.point_number<2:
            return None
        if endpoint == self.point_start:
            return self.points[1]
        if endpoint == self.point_end:
            return self.points[-2]
        raise ValueError(endpoint, "is not endpoint on", self)
    
    def merge_with(self, other:"Chain"):
        bl, br = self.blob_left, self.blob_right
        if not self.is_connected_to(other):
            raise ValueError("trying to merge two disconnected chains:", self, other)
        new_point_list:list[Point] = []
        common_point = self.common_endpoint(other)
       
        if self.point_start == common_point:
            self.points.reverse()
            #switch blob references
            self.swap_blob_references()
            bl, br = br, bl
        
        new_point_list.extend(self.points)
        new_point_list.pop() #the common point so that we don't add it twice
        if other.point_end == common_point:
            other.points.reverse()
        new_point_list.extend(other.points)

        other.unregister()
        self.points = new_point_list
        for point in new_point_list:
            point.chains.update([self])
        if br or bl:
            assert self.blob_right != self.blob_left
            
    def unregister(self):
        for point in self.points:
            point.chains.remove(self)
        # del self.points #might not be legal, if so just = []
        self.points = []
        self.unregister_from_blobs()
        # del self
    
    name:str = None

    def swap_blob_references(self):
        self.blob_left, self.blob_right = self.blob_right, self.blob_left
        if self.blob_right is not None and self.blob_right == self.blob_left:
            raise ValueError(self, "Chain references should not point to the same blob:", self.blob_left)
    