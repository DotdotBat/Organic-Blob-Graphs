from point import Point
from chain import Chain
from typing import List
from pygame.math import Vector2


class Intersection:
    def __init__(self, chains:List[Chain]) -> None:
        self.chains = []
        self.core: Point
        self.next_kin = []
        self.is_first_point = []
        #to connect chains properly 
        #we need to find out which point of the chain is to be connected to the intersection
        #so we are comparing the distance between the ends of the chains
        #and use the closest distance as a guide.
        a = chains[0]
        af = a.first_point.co
        al = a.last_point.co
        b = chains[1]
        bf = b.first_point.co
        bl = b.last_point.co
        ff = af.distance_squared_to(bf)
        fl = af.distance_squared_to(bl)
        lf = al.distance_squared_to(bf)
        ll = al.distance_squared_to(bl)
        # our first guess is that ff is smallest
        smallest_distance_so_far = ff
        guiding_point_candidate = a.first_point
        if(fl<smallest_distance_so_far):
            smallest_distance_so_far = fl
            guiding_point_candidate = a.first_point
        if(lf<smallest_distance_so_far):
            smallest_distance_so_far = lf
            guiding_point_candidate = a.last_point
        if(ll<smallest_distance_so_far):
            guiding_point_candidate = a.last_point

        guiding_point = guiding_point_candidate
        self.core = guiding_point
        for chain in chains:
            self.connect_chain_by_point(chain, guiding_point)
    
    chains: List[Chain]
    core: Point
    next_kin: List[Point]
    is_first_point: List[bool]

    def connect_chain_by_point(self, chain:Chain, point:Point):
        self.chains.append(chain)
        end_point_is_first = point == chain.first_point
        chain.add_point(point, append_to_start=end_point_is_first)
        self.is_first_point.append(end_point_is_first)
        neighbor_point:Point
        if end_point_is_first:
            neighbor_point = chain.points[1]
        else:
            neighbor_point = chain.points[-2]
        self.next_kin.append(neighbor_point)

    def keep_chains_connected(self):
        sum = Vector2(0,0)
        for end_point in self.core:
            sum+= end_point.co
        sum /= len(self.core)
        for end_point in self.core:
            x_off = sum.x - end_point.co.x
            y_off = sum.y - end_point.co.y
            end_point.add_offset(x_off,y_off)
    


        
        




