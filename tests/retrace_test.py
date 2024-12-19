from point import Point
from chain import Chain

def test_get_chained_points_lists_from_connected_points():
    p1 = Point(0,0)
    p2 = Point(1,1)
    p3 = Point(2,2)
    p4 = Point(3,3)
    points = [p1, p2, p3, p4]
    chained_points_lists = p1.get_chained_points_lists_from_connected_points()
    assert len(chained_points_lists) == 0, "No connections should mean no chains"

    # 1-2-3-4
    p1.connect_point(p2)
    p2.connect_point(p3)
    p4.connect_point(p3)
    chained_points_lists = p2.get_chained_points_lists_from_connected_points()
    assert len(chained_points_lists) ==1 
    chained_points = chained_points_lists[0]
    assert set(chained_points) == set(points) , "Not all points were traced"
    points_reversed = points.copy()
    points_reversed.reverse()

    assert chained_points == points or chained_points == points_reversed, "Point order was traced wrong"



def test_construct_chain_from_single_point():
    p1 = Point(0,0)
    p2 = Point(1,1)
    p3 = Point(2,2)
    points = [p1, p2, p3] #disconnected
    chains = Chain.construct_chains_from_point_connections(p1)
    assert len(chains) == 0, "No connections should mean no chains"

    #1-2-3
    p1.connect_point(p2)
    p2.connect_point(p3)
    chains = Chain.construct_chains_from_point_connections(p1)
    assert len(chains) ==1 
    chain = chains[0]
    assert type(chain) == Chain
    assert set(chain.points) == set(points) , "Not all points were traced"
    assert chain == Chain.from_point_list(points)



