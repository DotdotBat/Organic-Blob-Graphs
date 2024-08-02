from chain import Chain
from typing import List
from intersection import Intersection
width = 1280
height = 720
chains: List[Chain] = []
intersections: List[Intersection] = []
areas = []
min_length = min(width, height)
resolution = min_length /100
min_thinkness = min_length/10