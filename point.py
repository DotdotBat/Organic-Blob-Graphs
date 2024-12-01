from pygame.math import Vector2
class Point:
    def __init__(self, x, y) -> None:
        self.co = Vector2(x, y)
        self.offset = Vector2(0,0)
        self.chains = set()
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
        return any(chain.is_unmoving for chain in self.chains)
    
    chains= set()

    def mutually_repel(self, other:"Point", target_distance:float, ignore_unmoving = False):
        """try to move both points away from each other so that they will be a given distance apart"""
        
        initial_distance = self.co.distance_to(other.co)
        no_correction_is_required = initial_distance>target_distance
        if initial_distance<0.01:#Not enough information to repell, better not risk it
            no_correction_is_required = True 
        if not ignore_unmoving:
            if self.is_unmoving and other.is_unmoving:
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
        
        move_only_one_point = True #self.is_unmoving XOR other.is_unmoving
        ### SCENARIO 2
        if move_only_one_point:
            unmoving_point = self if self.is_unmoving else other
            moving_point = self if not self.is_unmoving else other
            # So if one is unmoving, the other has to move not half, but the full distance
            correction_amount = target_distance - initial_distance
            correction_direction = moving_point.co - unmoving_point.co
            correction_direction.scale_to_length(correction_amount)
            c = correction_direction
            moving_point.add_offset(c.x, c.y)
            #unmoving point doesn't get an offset
    
    is_unmoving_override:bool = None

    @property
    def chains_number(self):
        return len(self.chains)
    
    def endpoint_should_be_dissolved(self, ignore_umoving_status):
        "if it connects two different chains, and it is the endpoint of both, than the two chains act as one"
        if self.chains_number!=2:
            return False
        if not self.is_endpoint_on_all_chains:
            return False
        return True
        
    @property
    def is_endpoint_on_all_chains(self)->bool:
        #we do not consider scenarios where chains is empty, in a valid state, it will not be. 
        return all([self.is_endpoint_of_chain(chain) for chain in self.chains])

    
    @property
    def is_endpoint_on_ONLY_SOME_chains(self)->bool:
        if self.is_endpoint_on_all_chains:
            return False
        return any([self.is_endpoint_of_chain(chain) for chain in self.chains])
    
    is_endpoint_on_ONLY_SOME_chains
    
    def is_endpoint_of_chain(self, chain):
        return self == chain.point_start or self == chain.point_end
    
    def get_connected_points_via_chains(self) -> list["Point"]:
        adjacent_points = []
        if self.is_endpoint_on_all_chains:
            for chain in self.chains:
                adjacent_points.append(chain.endpoint_neighbor(self))
        else:
            #this isn't an endpoint, so it should have two neighboring points
            chain = list(self.chains)[0]
            self_index = chain.points.index(self)
            adjacent_points.append(chain.points[self_index-1])
            adjacent_points.append(chain.points[self_index+1])
        return adjacent_points
    
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

    def dissolve_endpoint(self):
        chains = list(self.chains)
        if self.is_endpoint_on_ONLY_SOME_chains:
            raise ValueError("invalid state")
        if len(chains) != 2:
            raise ValueError("Trying to dissolve a point that doesn't have exactly 2 chains", self, self.chains)
        longer_chain = chains[0] if chains[0].point_number > chains[1].point_number else chains[1]
        shorter_chain = chains[1] if chains[0] == longer_chain else chains[0]
        longer_chain.merge_with(shorter_chain)
            
    def get_common_chain(self, other:"Point"):
        if self == other:
            raise ValueError(self, "was passed as the other, must be unintended")
        chain_set = self.chains.intersection(other.chains)
        if len(chain_set) < 1:
            raise ValueError(self, "and", other, "don't have any chains in common") 
        

        chain_list = list(chain_set)
        if len(chain_list) > 1:
            #there might be more than one chain
            #in this case, we will return the shortest one
            chain_list = sorted(chain_list, key=lambda c: c.point_number)
        return chain_list[0]
    
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
    
    def assert_point_is_valid(self, check_local_chains_structure_too = True):        
        #are references to other points mutual? 
        for other in self.connected_points:
            other:"Point"
            assert self in other.connected_points , f"Non mutual connection between {self} and {other}"
        

        #does the local chain structure correspond to the point connections?
        if not check_local_chains_structure_too:
            return #stop here as chains are not correspoinding to point connection
        
        if len(self.connected_points)>0:
            assert len(self.chains)>0, "if Point has connected points, it means that it should be on a chain"

        assert self.connected_points == set(self.get_connected_points_via_chains()), "Connected points do not map correctly to local chain structure"




