from chain import Chain
from typing import List
from typing import Set
from blob import Blob
from point import Point

width = 1280
height = 720
chains: Set[Chain] = set()
areas = []
min_length = min(width, height)
resolution = min_length /100
min_thinkness = min_length/10

blobs_num = 3
blob_circumference = min_length

def ensure_chains_registered(check_chains:List[Chain]):
    chains.update(check_chains)
    
    for chain in chains:
            if not isinstance(chain, Chain):
                raise RuntimeError(chain)

frame_count = 0
outer_blob:Blob
inner_point = Point(width/2, height/2)