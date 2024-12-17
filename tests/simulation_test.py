from point import Point
from chain import Chain


def test_point_chains_references_management():
    # Step 1: Create some points
    p1 = Point(0, 0)
    p2 = Point(1, 0)
    p3 = Point(2, 0)
    p4 = Point(3, 0)
    p5 = Point(4, 0)
    p6 = Point(5, 0)
    points = [p1,p2,p3,p4,p5,p6]

    
    # Step 2: Create some chains from them
    chain1 = Chain.from_point_list([p1, p2])
    chain2 = Chain.from_coord_list([(10,40), (30, 20)])
    chain3 = Chain.from_end_points(p3, p4, point_num=3)
    chains = [chain1,chain2,chain3]
    def assert_chains_are_valid():
        for c in chains:
            c.assert_is_valid()
    
    # Step 3: Add a point to a chain
    chain1.append_endpoint(p5, append_to_start=False)
    assert_chains_are_valid()
    # Step 4: Remove a point from a chain
    chain1.remove_point(p2)
    chain3.remove_point(1)
    assert_chains_are_valid()
    # Step 5: Add a point from one chain to another chain
    chain1.append_endpoint(p3, append_to_start=True)
    assert_chains_are_valid()
    
    # Step 6: Swap a point on a chain for another point that wasn't on that chain
    chain1.swap_point(p1, p6)
    assert_chains_are_valid()

    
    # Step 7: create middle point
    midpoint = chain2.create_midpoint(0, 1)
    assert_chains_are_valid()
    points.append(midpoint)
    assert_chains_are_valid()

    #Step 8: cut chain into two
    chain2a, chain2b = chain2.cut(1)
    chains.append(chain2b)
    assert chain2a in chains
    assert_chains_are_valid()