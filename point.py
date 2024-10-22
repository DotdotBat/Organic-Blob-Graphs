from pygame.math import Vector2
class Point:
    def __init__(self, x, y) -> None:
        self.co = Vector2(x, y)
        self.offset = Vector2(0,0)
        self.chains = set()

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

    