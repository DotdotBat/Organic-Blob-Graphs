from typing import List
from chain import Chain
from point import Point
import math
import random
from list_util import rotate_list

class Blob:
    def __init__(self) -> None:
        self.chain_loop = list()
    
    @classmethod
    def from_chain_loop(cls, ccw_chain_loop:List[Chain], is_outer = False):
        if len(ccw_chain_loop)<2:
            raise NotImplementedError("We do not handle yet a case with so little chains", ccw_chain_loop)

        blob = cls()
        blob.chain_loop = ccw_chain_loop
    
        for chain_index, chain in enumerate(ccw_chain_loop):   
            blob_is_on_left_of_chain =  blob.is_chain_backwards(chain_index)
            if blob.is_clockwise():
                blob_is_on_left_of_chain = not blob_is_on_left_of_chain
            if is_outer:
                blob_is_on_left_of_chain = not blob_is_on_left_of_chain
            if blob_is_on_left_of_chain:
                chain.set_blobs(right=blob)
            else:
                chain.set_blobs(left=blob)
        return blob

    
    #keep this ordered.
    chain_loop:List[Chain]

    @property
    def intersection_indexes(self)->List[int]:
        """list of indexes of all intersections excluding the 0 one.
        This way the number of indexes is the same as the number of chains
        and each one corresponds to a single intersection."""
        sum = 0
        indexes = []
        for chain in self.chain_loop:
            sum+= len(chain.points) - 1
            indexes.append(sum)
        return indexes

    @property
    def points_num(self)->int:
        sum = 0
        for chain in self.chain_loop:
            sum+= len(chain.points)

        double_counted_endpoints_num = len(self.chain_loop)
        sum-= double_counted_endpoints_num
        return sum
    
    is_unmoving = False

    def get_chain_and_on_chain_point_index_at(self, point_index)->tuple[Chain, int]:
        point_index %= self.points_num
        intersections = [0] + self.intersection_indexes
        #find chain index using the intersections
        chain_index = 0
        for i, intersection in enumerate(intersections):
            if intersection >= point_index:
                break
            chain_index = i
        low_end = intersections[chain_index]
        high_end = intersections[chain_index+1]
        if self.is_chain_backwards(chain_index):
            chain_point_i = high_end - point_index
        else:
            chain_point_i = point_index - low_end
        chain = self.chain_loop[chain_index]
        return chain, chain_point_i

    def get_point(self, point_index:int):
        chain, on_chain_point_index = self.get_chain_and_on_chain_point_index_at(point_index)
        return chain.points[on_chain_point_index]

    def is_clockwise(self):
        points = []
        intersections_indexes = self.intersection_indexes
        prev_index = 0
        for i, index in enumerate(intersections_indexes):
            middle_chain_index = math.floor((prev_index+index)/2)
            points.append(self.get_point(middle_chain_index))
            points.append(self.get_point(index))
            prev_index = index 

        # Calculate the signed area using the Shoelace formula
        area = 0
        for i, p in enumerate(points):
            np = points[(i + 1) % len(points)]
            x1 = p.co.x
            x2 =np.co.x
            y1 = p.co.y
            y2 =np.co.y
            area += x1 * y2 - x2 * y1
        # If the signed area is positive, the points are in a clockwise order
        # its the oposite how it usually works because one axis (y) is flipped and the other isn't
        return area > 0
    
    def get_inner_direction(self, point_index, normalized = False):
        next_point = self.get_point(point_index+1)
        previous_point = self.get_point(point_index-1)
        v = next_point.co - previous_point.co
        if self.is_clockwise():
            return v.rotate(90)/2
        else:
            return v.rotate(-90)/2
        
    def spawn_small_blob(self, spawn_location:int|None = None) -> tuple["Blob", List[Chain]]:
        """Returns:
            The new blob : Blob
            A list of chains to be updated : List[Chain]
            """
        if spawn_location == None:
            spawn_location = random.randint(0, self.points_num)
        #consider picking a random chain intersection instead of a random point. 
        spawn_location %= self.points_num
        inset = self.get_inner_direction(spawn_location)
        s = self.get_point(spawn_location+1)
        self.cut_at(spawn_location+1)
        e = self.get_point(spawn_location-1)
        self.cut_at(spawn_location-1)
        new_chain_start_point = Point.from_point_and_offset(s, inset)
        new_chain_end_point = Point.from_point_and_offset(e, inset)
        new_chain = Chain.from_end_points(start=new_chain_start_point, end=new_chain_end_point, point_num=3)
        new_chain.add_point(s, append_to_start=True)
        new_chain.add_point(e, append_to_start=False)
        on_old_blob_chains = self.get_chains_between_intersections(
            start_index = spawn_location-1, 
            end_index = spawn_location + 1
            )
        self.swap_chains(chains_to_remove = on_old_blob_chains, chains_to_insert=[new_chain])
        new_blob_chains = on_old_blob_chains + [new_chain]
        new_blob = Blob.from_chain_loop(new_blob_chains)
        list_of_chains_to_update = new_blob.chain_loop + self.chain_loop
        
        self.set_blob_reference_on_chains()
        new_blob.set_blob_reference_on_chains()
        return new_blob, list_of_chains_to_update
    
    def get_chains_between_intersections(self, start_index, end_index):
        if not self.is_intersection_at(start_index):
            raise RuntimeError(start_index, "isn't an intersection")
        if not self.is_intersection_at(end_index):
            raise RuntimeError(end_index, "isn't an intersection")  
        if start_index == end_index:
            raise ValueError("this function was not designed to handle this scenario")
        
        _ , start_chain = self.get_chains_at_intersection(start_index)
        start_chain_index = self.chain_loop.index(start_chain)
        end_chain , _ = self.get_chains_at_intersection(end_index)

        i = start_chain_index
        current_chain = self.chain_loop[i]
        result = [start_chain]
        while current_chain != end_chain:
            i+=1
            i%=len(self.chain_loop)
            current_chain = self.chain_loop[i]
            result.append(current_chain)
        return result
                
    
    def is_intersection_at(self, point_index):
        point_index %= self.points_num
        point_count = 0
        for chain in self.chain_loop:
            if point_count == point_index:
                return True
            if point_count > point_index:
                return False
            point_count+= chain.points_number - 1
        return False
    
    def cut_at(self, point_index):
        if self.is_intersection_at(point_index):
            return self.get_chains_at_intersection(point_index)
        
        chain, on_chain_point_index = self.get_chain_and_on_chain_point_index_at(point_index)
        old_chain_index = self.chain_loop.index(chain)
        is_flipped = self.is_chain_backwards(chain)
        self.chain_loop.remove(chain)
        chain_start, chain_end = chain.cut(on_chain_point_index)
        if is_flipped:
            chain_start, chain_end = chain_end, chain_start
        self.chain_loop.insert(old_chain_index, chain_end)
        self.chain_loop.insert(old_chain_index, chain_start)

        if not self.is_intersection_at(point_index):
            raise RuntimeError("Cut method cut at the wrong place or the intersection check checks in the wrong place", point_index)

        self.is_valid(raise_errors=True)
        return chain_start, chain_end
    
    def get_chains_indexes_at_intersection(self, point_index:int):
        point_index %= self.points_num
        p_i = len(self.chain_loop) - 1
        # if point_index==self.points_num:
        #     return (p_i, 0)
        point_count = 0
        for n_i, next_chain in enumerate(self.chain_loop):
            if point_index == point_count:
                return (p_i, n_i)
            p_i = n_i
            point_count+=next_chain.points_number - 1
        raise ValueError("this place should not be reached at runtime")

    def get_chains_at_intersection(self, point_index:int):
        p_i, n_i = self.get_chains_indexes_at_intersection(point_index)
        previous_chain = self.chain_loop[p_i]
        next_chain = self.chain_loop[n_i]
        return previous_chain, next_chain

    def is_chain_backwards(self, chain:Chain|int)->bool:
        """if Chain is provided, the blob references are used to quickly determine the result.
        but if we are changing/setting them, or can not trust them. Use the chain index."""

        if type(chain) == int:
            chain_index = chain
            next_index = (chain_index + 1) % len(self.chain_loop)
            chain = self.chain_loop[chain_index]
            next_chain = self.chain_loop[next_index]
            if len(self.chain_loop)>2:
                common_point = chain.common_endpoint(next_chain)
                is_backwards = chain.point_start == common_point
                return is_backwards
            if len(self.chain_loop) == 2:
                #in a blob of two chains we will arbitrary decide that the first chain is in the right direction
                if chain_index == 0:
                    return False
                if chain_index == 1:
                    are_end_to_end = chain.point_end == next_chain.point_end
                    is_second_chain_backward = are_end_to_end
                    return is_second_chain_backward
            if len(self.chain_loop) == 1:
                return False
        
        chain:Chain
        if chain.blob_left == self:
            is_backwards = self.is_clockwise()
            return is_backwards
        elif chain.blob_right == self:
            is_backwards = not self.is_clockwise()
            return is_backwards
        else:
            chain_index = self.chain_loop.index(chain)
            return self.is_chain_backwards(chain_index)
 
    def swap_chains(self, chains_to_remove:List[Chain], chains_to_insert:List[Chain]):
        chlp = self.chain_loop[:]
        first_to_keep = chlp.index(chains_to_remove[-1]) + 1 
        rotation_amount = len(chlp) - first_to_keep
        chlp = rotate_list(chlp, -rotation_amount)
        for chain in chains_to_remove:
            chlp.pop()
        
        if not chlp[-1].is_connected_to(chains_to_insert[0]):
            chains_to_insert.reverse()

        if not (chlp[-1].is_connected_to(chains_to_insert[0])) or (not chlp[0].is_connected_to(chains_to_insert[-1])):
            print("that isn't right")
            raise RuntimeError("the chains to insert don't seem to have a common connection with the hole left from removing other chains in the swap operation")
            
        for chain in chains_to_insert:
            chlp.append(chain)

        chlp = rotate_list(chlp, rotation_amount)

        self.chain_loop = chlp[:]

    def is_valid(self, raise_errors = False):
        #todo: refactor into separate functions
        re = raise_errors
        if len(self.chain_loop)<1:
            if re: raise RuntimeError("Chain loop is empty")
            return False
            
        
        #loop connectivity check
        ########################
        if len(self.chain_loop) == 1:
            chain = self.chain_loop[0]
            if chain.point_start != chain.point_end:
                if re: raise ValueError("A single, non-circlular chain")
                return False

        prev_chain = self.chain_loop[-1]
        for chain in self.chain_loop:
            if not chain.is_connected_to(prev_chain):
                if re: raise RuntimeError(prev_chain, " is not connected to ", chain)
                return False
            prev_chain = chain
        if len(self.chain_loop) == 2:
            c1 = self.chain_loop[0]
            c2 = self.chain_loop[1]
            s_to_s = c1.point_start == c2.point_start
            e_to_e = c1.point_end == c2.point_end
            disconnected = False
            if s_to_s and not e_to_e:
                disconnected = True
            if e_to_e and not s_to_s:
                disconnected = True
            s_to_e = c1.point_start == c2.point_end
            e_to_s = c1.point_end == c2.point_start
            if s_to_e and not e_to_s:
                disconnected = True
            if e_to_s and not s_to_e:
                disconnected = True
            if disconnected:
                if re: raise ValueError("Blob of two chains is not circularly connected: ",self.chain_loop)
                return False

        #Blob_references on chains check
        is_cw = self.is_clockwise()
        blob_on_right_side = is_cw
        for i, chain in enumerate(self.chain_loop):
            blob_on_right_side_of_this_chain = blob_on_right_side
            if self.is_chain_backwards(i):
                blob_on_right_side_of_this_chain = not blob_on_right_side_of_this_chain
            if blob_on_right_side_of_this_chain:
                correct = (chain.blob_right == self) and (chain.blob_left  != self)
            else:
                correct = (chain.blob_left  == self) and (chain.blob_right != self)
            if not correct:
                if re: raise ValueError("on chain references are incorrectly set", chain, self)
                return False 

        return True
    
    area: float
    def recalculate_area(self):
        area = 0 
        for i in range(self.points_num):
            next_i = (i + 1) % self.points_num
            p1 = self.get_point(i)
            p2 = self.get_point(next_i)
            x1 = p1.co.x
            x2 = p2.co.x
            y1 = p1.co.y
            y2 = p2.co.y
            area += x1 * y2 - x2 * y1
        area/=2
        self.area =  abs(area)

    def set_blob_reference_on_chains(self):
        cw = self.is_clockwise()
        blob_is_to_the_left = not cw
        for i, chain in enumerate(self.chain_loop):
            backwards = self.is_chain_backwards(i)
            left = blob_is_to_the_left
            if backwards:
                left = not blob_is_to_the_left
            if left:
                chain.set_blobs(left=self)
            else:
                chain.set_blobs(right=self)
    
    def create_point_between_indexes(self, point_index:int, next_index:int)->Point:
        chain, chain_i, next_chain_i = self.get_chain_and_indexes_of_neighbors(point_index, next_index)
        new_point = chain.create_point_between_indexes(chain_i, next_chain_i)
        return new_point
    
    def get_chain_and_indexes_of_neighbors(self, point_i, next_i)->tuple[Chain, int, int]:
        chain_index = self.get_points_common_chain_index(point_i, next_i)
        iis = [0] + self.intersection_indexes
        low_i = iis[chain_index]
        high_i = iis[chain_index+1]
        if next_i == 0:
            next_i = self.points_num
        if not self.is_chain_backwards(chain_index):
            chain_point_i = point_i - low_i
            chain_next_point_i = next_i - low_i
        else:
            chain_point_i = high_i - point_i
            chain_next_point_i = high_i - next_i
        chain = self.chain_loop[chain_index]
        return chain, chain_point_i, chain_next_point_i

    def get_chains_indexes_at_point(self, point_index):
        point_index %= self.points_num
        intersections = [0] + self.intersection_indexes
        if point_index in intersections:
            chain1_i, chain2_i =  self.get_chains_indexes_at_intersection(point_index)
            return [chain1_i, chain2_i]
        
        chain_index = 0
        for i, intersection in enumerate(intersections):
            if intersection >= point_index:
                break
            chain_index = i
        return [chain_index]
    
    def get_chains_at_point(self, point_index):
        indexes = self.get_chains_indexes_at_point(point_index)
        chains =  [self.chain_loop[i] for i in indexes]
        return chains
    
    def get_points_common_chain_index(self, point1_index, point2_index):
        point1_chains_indexes = self.get_chains_indexes_at_point(point1_index)
        for chain_index in point1_chains_indexes:
            chain = self.chain_loop[chain_index]
            point2 = self.get_point(point2_index)
            is_common = point2 in chain.points
            if is_common:
                return chain_index
        raise RuntimeError("no common chain")
        
    def get_points_common_chain(self, point1_index, point2_index):
        chain_index = self.get_points_common_chain_index(point1_index, point2_index)
        return self.chain_loop[chain_index]
        