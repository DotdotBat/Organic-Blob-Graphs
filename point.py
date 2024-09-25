from pygame.math import Vector2
class Point:
    def __init__(self, x, y) -> None:
        self.co = Vector2(x, y)
        self.offset = Vector2(0,0)
        self.chains = set()

    def add_offset(self, x:float, y:float, multiplier=1):
        self.offset.x += x * multiplier
        self.offset.y += y * multiplier
    
    def apply_accumulated_offset(self):
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
    
    chains= set()
    
