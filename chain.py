from planar_graph import get_faces_of_planar_graph
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


    @classmethod
    def from_point_list(cls, points:Sequence["Point"], color = None) -> "Chain":
        chain = cls(color)
        chain.points = points[:] #list soft copy 
        #todo: connect point to it's neighbors
        for i, point in enumerate(chain.points):
            last_index = len(chain.points) - 1
            next_point = chain.points[i+1] if not i == last_index else None
            if next_point is None:
                break
            point.connect_point(next_point)
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
            t = i/(point_num-1)
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
        if self.point_number == 0:
            self.points.append(point)
            return
        if append_to_start:
            neighbor = self.point_start
            self.points.insert(0, point)
        else:
            neighbor = self.point_end
            self.points.append(point)
        neighbor.connect_point(point)
    
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

    @property
    def is_unmoving(self)->bool:
        if self.is_unmoving_override is not None:
            return self.is_unmoving_override
        if self.blob_left is None or self.blob_right is None:
            return True
        return self.blob_left.is_unmoving_override or self.blob_right.is_unmoving_override    
    
    
    def cut(self, point_index:int|Point):
        if type(point_index) is Point:
            point_index = self.points.index(point_index)
        if point_index <= 0 or point_index >= self.point_number - 1:
            raise ValueError("You are trying to cut too close to one of the ends of the chain. You are cutting at:", point_index, "While minimum is 1 and max is", self.point_number-2)
        start_points =  self.points[:point_index+1]
        end_points =    self.points[point_index:]
        self.points = start_points
        chain_start = self
        chain_end = Chain.from_point_list(points=end_points, color=self.color)
        assert chain_start.is_connected_to(chain_end)        
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
        mid_offset = (point.offset + next_point.offset)/2
        midpoint.offset = mid_offset
        midpoint.insert_between(point, next_point)
        self.points.insert(point_index+1, midpoint)
        return midpoint
    
    def remove_point(self, point:int|Point):
        if type(point) == int:
            point_index = point
            point = self.points[point_index]
        else:
            point_index =  point_index = self.points.index(point)
            point:Point
        last_index = len(self.points)-1
        if point_index>0 and point_index<last_index:
            previous_point = self.points[point_index-1]
            next_point = self.points[point_index+1]
            previous_point.connect_point(next_point)
        if point_index>0:
            previous_point = self.points[point_index-1]
            point.disconnect_point(previous_point)
        if point_index<last_index:
            next_point = self.points[point_index+1]
            point.disconnect_point(next_point)
        self.points.remove(point) 
        return point
    
    def swap_point(self, point_to_remove:Point, point_to_insert:Point):
        point_index = self.points.index(point_to_remove)
        point_to_insert.swap_connections_with(point_to_remove)
        self.points[point_index] = point_to_insert
    
    
    
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
        if br or bl:
            assert self.blob_right != self.blob_left
            
    def unregister(self):
        """removes the mutual references with both points and blobs"""
        # del self.points #might not be legal, if so just = []
        self.points.clear()
        self.unregister_from_blobs()
        # del self
    
    name:str = None

    def switch_endpoint_to(self, endpoint:Point, target:Point):
        is_start_point = endpoint == self.point_start
        self.remove_point(endpoint)
        self.append_endpoint(target, append_to_start=is_start_point)
        
    def assert_is_valid(self):
        assert self.point_number >= 2
        for i, point in enumerate(self.points):
            point.assert_point_is_valid()
            if i>0:
                previous_point = self.points[i-1]
                assert point.is_connected_to_point(previous_point)
        
        for point in self.points:
            if point not in [self.point_start, self.point_end]:
                assert len(point.connected_points) == 2, "inner chain points should not be intersections"
            

        
    @classmethod
    def construct_chains_from_point_connections(cls, point:Point):
        chained_points_lists = point.get_chained_points_lists_from_connected_points()
        all_connected_points = {point for chain in chained_points_lists for point in chain}
        new_chains = [cls.from_point_list(points) for points in chained_points_lists]
        return new_chains
    
    @staticmethod
    def find_all_endpoints(chains:list["Chain"]):
        endpoints = set()
        for chain in chains:
            if chain.point_number>0:
                endpoints.add(chain.point_start)
                endpoints.add(chain.point_end)
        return endpoints
    
    def __eq__(self, value:"Chain"):
        if self.points == value.points:
            return True
        rev = value.points.copy()
        rev.reverse()
        return self.points == rev
    
    def __hash__(self):
        if self.point_number < 2:
            return hash(Chain) + hash(str(self.points))
        if hash(self.point_start) < hash(self.point_end):
            return hash(Chain) + hash(str(self.points))
        else:
            points = self.points.copy()
            points.reverse()
            return hash(Chain) + hash(str(points))

    @staticmethod
    def are_collections_equivalent(col1, col2):
        col1, col2 = list(col1), list(col2)
        col1.sort(key=hash)
        col2.sort(key=hash)
        return col1 == col2
    
    @staticmethod
    def get_chain_loops_from_chains(chains:list["Chain"]):
        
        #constract_graph for traversal:
        points = set([c.point_start for c in chains] + [c.point_end for c in chains])
        verticies_to_points = {(point.co.x,point.co.y) : point for point in points}
        verticies = list(verticies_to_points.keys())
        edges = [((c.point_start.co.x,c.point_start.co.y), (c.point_end.co.x,c.point_end.co.y)) for c in chains]
        connections = dict()
        for v in verticies:
            connections[str(v)] = []
            connections
        for edge in edges:
            a, b = edge
            connections[str(a)].append(b)
            connections[str(b)].append(a)
        edge_loops = get_faces_of_planar_graph(graph_connections = connections, edges = edges)
        edge_loops:list[list[tuple[Point, Point]]]
        edge_to_chain = dict()
        for chain in chains:
            s = chain.point_start.co.x,chain.point_start.co.y
            e = chain.point_end.co.x,chain.point_end.co.y
            if str((s, e)) in edge_to_chain:
                raise NotImplementedError("Two chains have the same endpoints, this algoritm is not built to handle that")
                #The graph should be able to differentiate between the chains by a middlepoint
            edge_to_chain[str((s, e))] = chain
            edge_to_chain[str((e, s))] = chain
        faces = list()
        for edge_loop in edge_loops:
            face = [edge_to_chain[str(edge)] for edge in edge_loop]
            faces.append(face)
        return faces
        

        
