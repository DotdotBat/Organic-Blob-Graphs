from typing import Optional
from pygame.math import Vector2

def connect_point_list(points:list["Point"]):
    for i, point in enumerate(points):
        if i>0:
            previous_point = points[i-1]
            point.connect_point(previous_point)

class Point:
    def __init__(self, x, y) -> None:
        self.co = Vector2(x, y)
        self.offset = Vector2(0,0)
        self.connected_points = set()

    def add_offset(self, x:float, y:float, multiplier=1):
        self.offset.x += x * multiplier
        self.offset.y += y * multiplier
    
    def apply_accumulated_offset(self, ignore_unmoving = False):
        if (not ignore_unmoving) and self.is_unmoving:
            return
        self.co+=self.offset
        self.offset.update(0,0)

    def __str__(self) -> str:
        return f'Point at {self.co}'
    
    __repr__ = __str__
    
    @classmethod
    def from_point_and_offset(cls, point:"Point", offset:Vector2):
        co = point.co + offset
        return cls(co.x, co.y)
    
    def clamp_offset(self, clamp_value):
        if self.offset.length_squared() > clamp_value*clamp_value:
            self.offset.scale_to_length(clamp_value)
    
    @property
    def is_unmoving(self):
        if self.is_unmoving_override is not None:
            return self.is_unmoving_override
        return False
    
    def mutually_repel(self, other:"Point", target_distance:float, ignore_unmoving = False):
        """try to move both points away from each other so that they will be a given distance apart"""
        
        initial_distance = self.co.distance_to(other.co)
        no_correction_is_required = initial_distance>target_distance
        if initial_distance<0.01:#Not enough information to repell, better not risk it
            no_correction_is_required = True 
        if not ignore_unmoving and self.is_unmoving and other.is_unmoving:
            no_correction_is_required = True

        ### SCENARIO 0
        if no_correction_is_required:
            return

        should_move_both_points = not (self.is_unmoving or other.is_unmoving)
        if ignore_unmoving: should_move_both_points = True
        ### SCENARIO 1
        if should_move_both_points: 
            correction_amount = (target_distance - initial_distance)/2
            correction_direction = other.co - self.co
            correction_direction.scale_to_length(correction_amount)
            c = correction_direction
            self.add_offset(-c.x, -c.y)
            other.add_offset(+c.x, +c.y)
            return

        #we can reach this line only and only if just one of the points is unmoving
        # also ignore unmoving would have triggered the move_both_points scenario 
        
        
        ### SCENARIO 2 - move only one point

        unmoving_point = self if self.is_unmoving else other
        moving_point = self if not self.is_unmoving else other
        # So if one is unmoving, the other has to move not half, but the full distance
        correction_amount = target_distance - initial_distance
        correction_direction = moving_point.co - unmoving_point.co
        correction_direction.scale_to_length(correction_amount)
        c = correction_direction
        moving_point.add_offset(c.x, c.y)
        #unmoving point doesn't get an offset
    
    is_unmoving_override:Optional[bool] = None
    
    

    
    def is_endpoint_of_chain(self, chain):
        return self == chain.point_start or self == chain.point_end
    

    
    def closest_of_points(self, others:list["Point"], dont_ignore_self=False):
        if not dont_ignore_self and self in others:
            others= others.copy()
            others.remove(self)
        if len(others)<1:
            raise ValueError("Nothing to compare to in ", others)
        closest = others[0]
        for other in others:
            if self.co.distance_squared_to(other.co) < self.co.distance_squared_to(closest.co):
                closest = other
        return closest
    
    def connect_point(self, other:"Point"):
        if other == self:
            raise ValueError("Tried to connect to self", self)
        self.connected_points.add(other)
        other.connected_points.add(self)
    
    def disconnect_point(self, other:"Point"):
        if self.is_connected_to_point(other):
            self.connected_points.remove(other)
            other.connected_points.remove(self)
    
    def is_connected_to_point(self, other:"Point"):
        if self in other.connected_points or other in self.connected_points:
            if not (self in other.connected_points and other in self.connected_points):
                raise RuntimeError("non mutual connection:", self, other)
            return True
        return False
    
    def assert_point_is_valid(self):        
        #are references to other points mutual? 
        for other in self.connected_points:
            other:"Point"
            assert self in other.connected_points , f"Non mutual connection between {self} and {other}"
        
       
    def _is_intersection_or_dead_end(self):
            return len(self.connected_points) != 2
    
    def _traverse_to_an_intersection_or_dead_end(self)->"Point":
            if self._is_intersection_or_dead_end():
                return self
            previous = self
            current = list(self.connected_points)[0]
            while (not current._is_intersection_or_dead_end()):
                directions = list(current.connected_points)
                directions.remove(previous) #only forwards!
                next_point = directions[0]
                previous = current
                current = next_point
                if current == self:
                    break
            return current
    
    def get_chained_points_lists_from_connected_points(self)->list[list["Point"]]:
        chained_point_lists = []
        explored_directions = []
        unexplored_directions = []
        root_point = self._traverse_to_an_intersection_or_dead_end()
        for neighbor in root_point.connected_points:
            direction = (root_point, neighbor)
            unexplored_directions.append(direction)
        while len(unexplored_directions) > 0:
            node, neighbor = direction = unexplored_directions.pop()
            chained_points = node.get_chained_list_in_direction(neighbor)
            chained_point_lists.append(chained_points)
            explored_directions.append(direction)
            twin_direction = chained_points[-1], chained_points[-2]
            explored_directions.append(twin_direction)
            if twin_direction in unexplored_directions:
                unexplored_directions.remove(twin_direction)
            endpoint = chained_points[-1]
            for neighbor in endpoint.connected_points:
                direction = endpoint, neighbor
                if direction not in explored_directions and direction not in unexplored_directions:
                    unexplored_directions.append(direction)
        return chained_point_lists
 
    def dismantle_structure(self):
        neigbors = self.connected_points.copy()
        self.connected_points.clear()
        for p in neigbors:
            p.dismantle_structure()
    
    def insert_between(self, a:"Point", b:"Point"):
        a.disconnect_point(b)
        self.connect_point(a)
        self.connect_point(b)


    def swap_connections_with(self, other:"Point"):
        others_points = other.connected_points.copy()
        selfs_points = self.connected_points.copy()

        for point in others_points:
            other.disconnect_point(point)
        for point in selfs_points:
            self.disconnect_point(point)
        for point in selfs_points:
            other.connect_point(point)
        for point in others_points:
            self.connect_point(point)
        
    @classmethod
    def from_coordinates(cls, x:float, y:float):
        return cls(x, y)
    
    def get_chained_list_in_direction(self, direction:"Point"):
        a, b = self, direction
        l = [a, b]
        while len(b.connected_points) == 2 and b is not self:
            b_connections = list(b.connected_points)
            b_connections.remove(a)
            c = b_connections[0]
            l.append(c)
            a, b = b, c
        return l
