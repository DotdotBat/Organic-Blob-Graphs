import warnings
from chain import Chain
from point import Point

from typing import List, Optional
import math
import random
from list_util import rotate_list

class Blob:
    """Blob is a a data structure holding a chain loop. Each chain consists of points. So you can think of blobs as a point rings. Chains can be forward or backward depending on whether their inner order of points aligns with the blob's chain loop. Or you can think of blobs as a representaion of 2d bubbles, where chains are the shared edges between the bubbles."""
    def __init__(self) -> None:
        self.chain_loop = list()
        
    
    @classmethod
    def from_chain_loop(cls, ccw_chain_loop:List[Chain]):
        blob = cls()
        blob.chain_loop = ccw_chain_loop.copy()
        return blob

    
    #keep this ordered.
    chain_loop:List[Chain]

    @property
    def intersection_indexes(self)->List[int]:
        """list of indexes of all intersections excluding the 0 one.
        This way the number of indexes is the same as the number of chains
        and each one corresponds to a single intersection."""
        i = 0
        indexes = []
        for chain in self.chain_loop:
            i+= len(chain.points) - 1
            indexes.append(i)
        return indexes

    @property
    def point_number(self)->int:
        i = 0
        for chain in self.chain_loop:
            i+= len(chain.points)

        double_counted_endpoints_num = len(self.chain_loop)
        i-= double_counted_endpoints_num
        return i
    
    is_unmoving_override = False

    def get_chain_and_on_chain_point_index_at(self, point_index)->tuple[Chain, int]:
        point_index %= self.point_number
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

    def get_point(self, point_index:int)->Point:
        chain, on_chain_point_index = self.get_chain_and_on_chain_point_index_at(point_index)
        return chain.points[on_chain_point_index]

    def is_clockwise(self):
        points = []
        if len(self.chain_loop) > 2:

            intersections_indexes = self.intersection_indexes
            prev_index = 0
            for i, intersection_index in enumerate(intersections_indexes):
                middle_chain_index = math.floor((prev_index+intersection_index)/2)
                points.append(self.get_point(middle_chain_index))
                points.append(self.get_point(intersection_index))
                prev_index = intersection_index 
        elif self.point_number<10:
            points = self.points_list
        else:
            sample_number = 10
            for i in range(sample_number):
                intersection_index = math.floor((i/sample_number)*self.point_number)
                points.append(self.get_point(intersection_index))
            
            
            

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
    
    def get_inner_direction(self, point_index):
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
            spawn_location = random.randint(0, self.point_number)
        #consider picking a random chain intersection instead of a random point. 
        spawn_location %= self.point_number
        inset = self.get_inner_direction(spawn_location)
        s = self.get_point(spawn_location+1)
        self.cut_at(spawn_location+1)
        e = self.get_point(spawn_location-1)
        self.cut_at(spawn_location-1)
        new_chain_start_point = Point.from_point_and_offset(s, inset)
        new_chain_end_point = Point.from_point_and_offset(e, inset)
        new_chain = Chain.from_end_points(start=new_chain_start_point, end=new_chain_end_point, point_num=3)
        new_chain.append_endpoint(s, append_to_start=True)
        new_chain.append_endpoint(e, append_to_start=False)
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
        new_blob.link_length = self.link_length
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
        point_index %= self.point_number
        point_count = 0
        for chain in self.chain_loop:
            if point_count == point_index:
                return True
            if point_count > point_index:
                return False
            point_count+= chain.point_number - 1
        return False
    
    def cut_at(self, point_index):
        if self.is_intersection_at(point_index):
            return self.get_chains_at_intersection(point_index)
        chain, on_chain_point_index = self.get_chain_and_on_chain_point_index_at(point_index)
        chain_index = self.chain_loop.index(chain)
        flip = self.is_chain_backwards(chain_index=chain_index)
        chain_start, chain_end = chain.cut(on_chain_point_index)
        if flip:
            chain_start, chain_end = chain_end, chain_start
        self.chain_loop[chain_index] = chain_end
        self.chain_loop.insert(chain_index, chain_start)
        return chain_start, chain_end
    
    def get_chains_indexes_at_intersection(self, point_index:int):
        point_index %= self.point_number
        p_i = len(self.chain_loop) - 1
        point_count = 0
        for n_i, next_chain in enumerate(self.chain_loop):
            if point_index == point_count:
                return (p_i, n_i)
            p_i = n_i
            point_count+=next_chain.point_number - 1
        raise ValueError("this place should not be reached at runtime")

    def get_chains_at_intersection(self, point_index:int):
        p_i, n_i = self.get_chains_indexes_at_intersection(point_index)
        previous_chain = self.chain_loop[p_i]
        next_chain = self.chain_loop[n_i]
        return previous_chain, next_chain

    def is_chain_backwards(self, chain:Chain= None, chain_index:int = None)->bool:
        """if Chain is provided, the blob references are used to quickly determine the result.
        but if we are changing/setting them, or can not trust them. Use the chain index."""
        if len(self.chain_loop) == 1:
                return False #there is only one chain - of course it isn't backwards
        if isinstance(chain, int):
            chain_index = chain
            chain = None
        if chain_index == None:
            chain_index = self.chain_loop.index(chain)
            return self.is_chain_backwards(chain_index = chain_index)
        if chain == None:
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
        raise RuntimeError("Shouldn't have reached this point, most likely an argument type error")    
        
 
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

    def assert_loop_is_connected(self):
        if len(self.chain_loop) == 1:
            chain = self.chain_loop[0]
            assert chain.point_start == chain.point_end, "Blob composed of a single, non-circlular chain"

        prev_chain = self.chain_loop[-1]
        for chain in self.chain_loop:
            assert chain.is_connected_to(prev_chain), f"{prev_chain} is not connected to {chain}"
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
            assert not disconnected ,f"Blob of two chains is not circularly connected: {self.chain_loop}"

    def assert_is_valid(self):
        assert len(self.chain_loop)>0 , "Chain loop is empty"
        
        for chain in self.chain_loop:
            chain.assert_is_valid()
        
        self.assert_loop_is_connected()
        

    remembered_rough_centroid_xy:tuple[float, float] = (math.inf, math.inf)
    @property
    def area(self):
        actual_rough_centroid = self.rough_centroid_xy
        if self.remembered_rough_centroid_xy != actual_rough_centroid:
            self.remembered_rough_centroid_xy = actual_rough_centroid
            self.cashed_area = None
        if self.cashed_area is None:
            self.cashed_area = self.calculate_area()
        return self.cashed_area
    cashed_area: float
    def calculate_area(self):
        area = 0 
        for i in range(self.point_number):
            next_i = (i + 1) % self.point_number
            p1 = self.get_point(i)
            p2 = self.get_point(next_i)
            x1 = p1.co.x
            x2 = p2.co.x
            y1 = p1.co.y
            y2 = p2.co.y
            area += x1 * y2 - x2 * y1
        area/=2
        return abs(area)

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
    
    def create_midpoint(self, point_index:int, next_index:int)->Point:
        chain, chain_point_i, next_chain_point_i = self.get_chain_and_indexes_of_neighbors(point_index, next_index)
        new_point = chain.create_midpoint(chain_point_i, next_chain_point_i)
        return new_point
    
    def get_chain_and_indexes_of_neighbors(self, point_i:int, next_i:int)->tuple[Chain, int, int]:
        chain_index = self.get_points_common_chain_index(point_i, next_i)
        iis = [0] + self.intersection_indexes
        low_i = iis[chain_index]
        high_i = iis[chain_index+1]
        if next_i == 0:
            next_i = self.point_number
        if not self.is_chain_backwards(chain_index):
            chain_point_i = point_i - low_i
            chain_next_point_i = next_i - low_i
        else:
            chain_point_i = high_i - point_i
            chain_next_point_i = high_i - next_i
        chain = self.chain_loop[chain_index]
        return chain, chain_point_i, chain_next_point_i

    def get_chains_indexes_at_point(self, point_index):
        point_index %= self.point_number
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
    
    def _common_chain_index_of_2_chain_loop_when_both_intersections_are_given(self, point1_index):
        chain1, chain2 = self.chain_loop
        if chain1.point_number != chain2.point_number:
            common_chain = chain1 if chain1.point_number<chain2.point_number else chain2
        else:
            common_chain= chain2 if point1_index != 0 else chain1
        return 0 if common_chain==chain1 else 1
    
    def get_points_common_chain_index(self, point1_index, point2_index):
        #special case:
        if len(self.chain_loop) ==2 and self.is_intersection_at(point1_index) and self.is_intersection_at(point2_index):
            self._common_chain_index_of_2_chain_loop_when_both_intersections_are_given(point1_index)

        point1_chains_indexes = self.get_chains_indexes_at_point(point1_index)
        for chain_index in point1_chains_indexes:
            chain = self.chain_loop[chain_index]
            point2 = self.get_point(point2_index)
            is_common = point2 in chain.points
            if is_common:
                return chain_index
        
    def get_points_common_chain(self, point1_index, point2_index):
        chain_index = self.get_points_common_chain_index(point1_index, point2_index)
        return self.chain_loop[chain_index]
    
    def neighboring_indexes(self, point_index:int)->tuple[int, int]:
        prev_index = (point_index - 1)% self.point_number
        next_index = (point_index + 1)% self.point_number
        return prev_index, next_index
        
    def remove_point(self, point_index):
        if not self.is_intersection_at(point_index):
            chain, chain_point_index = self.get_chain_and_on_chain_point_index_at(point_index)
            return chain.remove_point(chain_point_index)
        
        #so this is an intersection. 
        #Then we should merge its connections to a neighbor
        
        _, next_index = self.neighboring_indexes(point_index)
        point = self.get_point(point_index)
        next_point = self.get_point(next_index)
        common_chain = self.get_points_common_chain(point_index, next_index)
        point_chains = point.chains.copy()
        for chain in point_chains:
            chain:Chain
            if chain == common_chain:
                common_chain.remove_point(point)
                if common_chain.point_number < 2:
                    common_chain.unregister()
            else:
                chain.swap_point(point_to_remove=point, point_to_insert=next_point)
        return point
    
    def find_biggest_gap_indexes(self, only_movable_chains = True):
        longest_gap_length_on_blob = 0
        gap_index_pair = (-1, -1)
        for chain in self.chain_loop:
            if only_movable_chains and chain.is_unmoving:
                continue #skip the chain
            i, next_i, gap_length = chain.find_biggest_gap() 
            if gap_length> longest_gap_length_on_blob:
                longest_gap_length_on_blob = gap_length
                index = chain.get_on_blob_point_index(blob=self, chain_point_index=i)
                other_index = chain.get_on_blob_point_index(blob=self, chain_point_index=next_i)
                gap_index_pair = (index, other_index)
                if self.is_chain_backwards(chain):
                    gap_index_pair = (other_index, index)

        index, next_index = gap_index_pair
        return index, next_index
    
    def find_most_crowded_point_index(self):
        smallest_sum = math.inf
        for point_index in range(self.point_number):
            prev_index, next_index = self.neighboring_indexes(point_index)
            prev_point = self.get_point(prev_index)
            point = self.get_point(point_index)
            next_point = self.get_point(next_index)
            prev_gap = point.co.distance_squared_to(prev_point.co)
            next_gap = point.co.distance_squared_to(next_point.co)
            index_sum = prev_gap + next_gap
            if index_sum < smallest_sum:
                i = point_index
                smallest_sum = index_sum
        return i

    def modify_point_number(self, delta_num):
        if self.point_number<=3 and delta_num<0:
                    return

        iteration_number = abs(delta_num)
        for _ in range(iteration_number):
            if delta_num > 0:
                point_index, next_index = self.find_biggest_gap_indexes()
                self.create_midpoint(point_index, next_index)
            else:
                point_index = self.find_most_crowded_point_index()
                self.remove_point(point_index)

    def index_distance(self, index_a:int, index_b:int):
        """given the indexes of two points returns the shortest of the two distances between them in index difference"""
        normal_difference = abs(index_a - index_b)
        round_about_difference = self.point_number-normal_difference
        return min(normal_difference, round_about_difference)

    def circumference_distance(self, index_a:int, index_b:int, link_length):
        """given the indexes of two points returns the shortest of the two distances along the circumference of the blob (like arcs)"""
        return link_length * self.index_distance(index_a, index_b)
    
    def points_distance(self, point_index, other_index):
        """given the indexes of two points returns the spacial distance between them"""
        point, other = self.get_point(point_index), self.get_point(other_index)
        return point.co.distance_to(other.co)
    

    @property
    def points_list(self)->list[Point]:
        return [self.get_point(index) for index in range(self.point_number)]
    
    @property
    def actual_circumference(self)->float:
        s = 0
        for i in range(self.point_number):
            _, n = self.neighboring_indexes(i)
            s += self.points_distance(i, n)
        return s
    
    @property
    def link_length(self)->float:
        if self._stored_link_length == 0:
            print("blob didn't know it's link length, so it just calculated it on the fly, and will remember it")
            self._stored_link_length = self.actual_circumference/self.point_number
        return self._stored_link_length
    _stored_link_length = 0
    @link_length.setter
    def link_length(self, length:float):
        self._stored_link_length = length

    def find_local_minimum_width_pair_under_target_width(self, sample_number:int, index_berth:int, target_width:float):
        """Will semi efficiently find the local minimum width and return the pair of indexes and the width.
        if the found width is larger than the target width, returns -1, -1 and a width that most likely isn't the smallest"""
        #helper function
        def initial_pairs(number_of_pairs:int):
            pairs = []
            for i in range(number_of_pairs):
                a = math.floor(0.5 *self.point_number*i/number_of_pairs)
                b = (self.point_number//2 + a)%self.point_number
                pairs.append((a,b))
            return pairs

        #----------main-----------
        smallest_width_so_far = math.inf
        initial_guesses = initial_pairs(number_of_pairs=sample_number)
        closest_pair=(-3, -3)
        for pair in initial_guesses:
            found_local_minimum = False
            closer_pair = pair
            while not found_local_minimum:
                closer_pair, distance = self.try_finding_closer_pair(closer_pair,index_berth=index_berth, target_distance=target_width)
                found_local_minimum = closer_pair == (-404, -404) #a code meaning that we have reached the local minimum, the privious pair was the closest so we can get out of the loop
                if distance<smallest_width_so_far:
                    smallest_width_so_far = distance
                    closest_pair = closer_pair
        index_a, index_b = closest_pair
        smallest_width = smallest_width_so_far
        if smallest_width > target_width:
            return -1, -1, smallest_width
        return index_a, index_b, smallest_width

    def try_finding_closer_pair(self, initial_pair:tuple[int,int],index_berth:int, target_distance:float):
        """will search in the vacinity, but if the given pair looks like the closest pair seems to be the initial one, it will return the initial one"""
        #helper function
        def create_candidate_pairs_list(blob:Blob, base_pair:tuple[int, int], step:int, index_berth:int):
            index_a, index_b = base_pair
            a_indexes = [index_a, (index_a-step)%blob.point_number, (index_a+step)%blob.point_number]
            b_indexes = [index_b, (index_b-step)%blob.point_number, (index_b+step)%blob.point_number]
            candidate_pairs = [(a, b) for a in a_indexes for b in b_indexes]
            candidate_pairs.remove(base_pair)
            valid_pairs = [pair for pair in candidate_pairs if blob.index_distance(*pair)>index_berth]
            return valid_pairs
        
        
        #---------main-------
        step:int
        initial_distance = self.points_distance(*initial_pair)
        if target_distance>initial_distance:
            step = 1
        else:
            step = math.ceil((initial_distance - target_distance)/self.link_length)
        candidate_pairs = create_candidate_pairs_list(blob= self, base_pair=initial_pair, step=step, index_berth=index_berth)
        closest_pair = initial_pair
        smallest_distance = initial_distance
        for candidate in candidate_pairs:
            candidate_distance = self.points_distance(*candidate)
            if candidate_distance<smallest_distance:
                smallest_distance = candidate_distance
                closest_pair = candidate
        if closest_pair == initial_pair:
            closest_pair = (-404,-404) #a code that we have reached the local minimum
        return closest_pair, smallest_distance
    
    
    def apply_accumulated_offsets(self, ignore_unmoving_status=False):
        for chain in self.chain_loop:
            chain.apply_accumulated_offsets(ignore_unmoving_status=ignore_unmoving_status)
    
    def opposite_index(self, point_index):
        point_number = self.point_number
        return (point_index+point_number//2)%point_number

    name:Optional[str] = None
    
    def __str__(self) -> str:
        named = ""
        if self.name is not None:
            named = self.name+" "
        info = f'{named}Blob with {len(self.chain_loop)} chains and {self.point_number} points'
        if self.point_number>0:
            info = info + f' at {self.get_point(0).co.xy}'
        return info

    def __repr__(self):
        obj_id = id(self)
        hex_addr = hex(obj_id)[2:]  # Remove '0x' prefix
        return f"<{str(self)} at 0x{hex_addr}>"

    def __eq__(self, value):
        if type(value) != type(self):
            return False
        my_points = self.points_list.copy()
        your_points = value.points_list.copy()
        for point_list in [my_points, your_points]:
            if point_list[0] == point_list[-1]:
                #a special case of a blob of only one chain, will not come up in real scenarios, it is easier to work around it than build on it. 
                point_list.pop()
        first_point = my_points[0]
        if first_point not in your_points:
            return False
        first_point_index = your_points.index(first_point)
        your_points = rotate_list(your_points, first_point_index)
        assert my_points[0] == your_points[0]
        if my_points[1] != your_points[1]:
            your_points = rotate_list(your_points, 1)
            your_points.reverse()
        return my_points == your_points

    @classmethod
    def construct_blobs_from_chains(cls, chains:list[Chain]):
        chain_loops = Chain.get_chain_loops_from_chains(chains)
        blobs = [Blob.from_chain_loop(chain_loop) for chain_loop in chain_loops]
        return blobs
    
    def hash(self):
        x, y = self.true_centroid
        return hash((self.point_number, self.area, x, y))
    
    @property
    def rough_centroid_xy(self):
        '''isn't accurate, but efficient and deterministic'''
        points = self.points_list
        point_number = self.point_number
        representatives_number = math.ceil(math.log2(point_number))
        sum_x, sum_y = 0, 0
        for r in range(representatives_number):
            i = r * math.floor(point_number//representatives_number)
            rp = points[i] #representative point
            sum_x+= rp.co.x
            sum_y+= rp.co.y
        sum_x/=representatives_number
        sum_y/=representatives_number
        return (sum_x, sum_y)

    @staticmethod
    def are_collections_equivalent(col1, col2):
        col1, col2 = list(col1), list(col2)
        col1.sort(key=lambda b:b.hash())
        col2.sort(key=lambda b:b.hash())
        for a, b in zip(col1, col2):
            if a != b: 
                return False
        return True
    
    @property
    def true_centroid(self):
        sum_x = sum(p.co.x for p in self.points_list)
        sum_y = sum(p.co.y for p in self.points_list)
        x, y = sum_x/self.point_number, sum_y/self.point_number
        return (x, y)
