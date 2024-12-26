from blob import Blob
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


def test_single_chain_loop_retracing():
    blob = create_valid_blob()
    point = blob.get_point(0)
    chains = Chain.construct_chains_from_point_connections(point)
    assert len(chains) == 1
    chain = chains[0]
    assert chain.point_start == chain.point_end
    chain_loops = Chain.get_chain_loops_from_chains(chains) 
    assert len(chain_loops) == 1
    chain_loop = chain_loops[0]
    blob = Blob.from_chain_loop(chain_loop)
    blob.assert_is_valid()
    c1, c2 = chain.cut(chain.point_number//2)
    c2, c3 = c2.cut(c2.point_number//2)
    chains = [c1, c2, c3]
    chain_loops = Chain.get_chain_loops_from_chains(chains)
    assert len(chain_loops) == 1
    chain_loop = chain_loops[0]
    blob2 = Blob.from_chain_loop(chain_loop)
    blob2.assert_is_valid()
    assert blob == blob2


from blob_test import create_valid_blob
def test_reconstruct_a_blob():
    blob = create_valid_blob()
    point = blob.get_point(0)
    chains = Chain.construct_chains_from_point_connections(point)
    assert len(chains) == 1
    chain = chains[0]
    assert chain.point_start == chain.point_end
    chain_loops = Chain.get_chain_loops_from_chains(chains) 
    assert len(chain_loops) == 1
    # reconstracted_blobs = Blob.construct_blobs_from_chains(chains)
    # assert len(reconstracted_blobs) == 1
    # reconstracted_blob = reconstracted_blobs[0]
    # assert blob.point_number == reconstracted_blob.point_number
    # assert reconstracted_blob == blob
    # blob.assert_is_valid()
    # reconstracted_blob.assert_is_valid()
    



