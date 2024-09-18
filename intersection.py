from point import Point
from chain import Chain
from typing import List
from enum import Enum

class chain_point(Enum):
    START = 1
    END = 2

class Intersection:
    def __init__(self) -> None:
        self.chains = []
        self.chain_connected_by = [] 
        """chain_point.START or chain_point.END"""


    chains: List[Chain]
    connection_point: Point
    

    def connect_chain(self, chain:Chain):
        if chain in self.chains:
            return
        
        self.chains.append(chain)
        connecting_by_start_point = self.connection_point == chain.point_start
        if connecting_by_start_point:
            self.chain_connected_by.append(chain_point.START)
            chain.intersection_start = self
        else:
            self.chain_connected_by.append(chain_point.END)
            chain.intersection_end = self
                

    @classmethod
    def from_point_and_chain_list(cls, connection_point:Point, chains:List[Chain]):
        intersection = cls()
        intersection.connection_point = Point
        




        
        




