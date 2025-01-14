import pytest
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
    assert isinstance(chain, Chain)
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
    reconstructed_blob = Blob.from_chain_loop(chain_loop)
    reconstructed_blob.assert_is_valid()
    assert reconstructed_blob == blob

    c1, c2 = chain.cut(chain.point_number//2)
    c2, c3 = c2.cut(c2.point_number//2)
    #such mutulation of the reconstructed blob chains, without notifying the reconstracted blob, breaks it
    with pytest.raises(AssertionError):
        reconstructed_blob.assert_is_valid()
    
    chains = [c1, c2, c3]
    chain_loops = Chain.get_chain_loops_from_chains(chains)
    assert len(chain_loops) == 1
    chain_loop = chain_loops[0]
    blob2 = Blob.from_chain_loop(chain_loop)
    blob2.assert_is_valid()
    assert blob == blob2

def test_multiple_connected_chain_loops_chain_retracing():
    points, chains, _ = create_valid_blob_collection()
    
    new_chains = Chain.construct_chains_from_point_connections(points[0])
    new_points = set()
    for chain in new_chains:
        new_points.update(chain.points)
    assert set(points) == new_points
    assert Chain.are_collections_equivalent(chains, new_chains)

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
    reconstracted_blobs = Blob.construct_blobs_from_chains(chains)
    assert len(reconstracted_blobs) == 1
    reconstracted_blob = reconstracted_blobs[0]
    assert blob.point_number == reconstracted_blob.point_number
    assert reconstracted_blob == blob
    blob.assert_is_valid()
    reconstracted_blob.assert_is_valid()
    
from blob_test import create_valid_blob_collection, assert_no_doubles_in_list

def test_reconstruct_a_blob_collection():
    points, chains, blobs = create_valid_blob_collection()
    root_point = points[0]
    new_chains = Chain.construct_chains_from_point_connections(root_point)
    assert_no_doubles_in_list(new_chains)
    assert len(new_chains) == len(chains)
    assert Chain.are_collections_equivalent(chains, new_chains)
    new_blobs = Blob.construct_blobs_from_chains(new_chains)
    assert Blob.are_collections_equivalent(blobs, new_blobs)
    for objects in [points, new_chains, new_blobs]:
        assert_no_doubles_in_list(objects)
        for o in objects:
            o.assert_is_valid()

def test_reconstruct_blobs_when_they_all_share_two_points():
    p1, p2 = Point(-10, 0), Point(10, 0)
    
    middle_points = [Point.from_coordinates(0, i) for i in range(-10, 11)]

    for mp in middle_points:
        mp.connect_point(p1)
        mp.connect_point(p2)
    
    chains = Chain.construct_chains_from_point_connections(p1)
    assert_no_doubles_in_list(chains)
    assert len(chains) == len(middle_points)
    for chain in chains:
        assert chain.point_number == 3
        assert chain.points[1] in middle_points
    blobs = Blob.construct_blobs_from_chains(chains)
    for blob in blobs:
        assert len(blob.chain_loop) == 2
    
    for i, mp in enumerate(middle_points):
        expected_occurrence_number = 2
        if i == 0 or i == len(middle_points) -1:
            expected_occurrence_number = 1
        occurrence_count = 0
        for blob in blobs:
            if mp in blob.points_list:
                occurrence_count += 1
        assert occurrence_count == expected_occurrence_number

    for blob in blobs:
        points = blob.points_list.copy()
        points.remove(p1)
        points.remove(p2)
        assert len(points) == 2
        i1, i2 = middle_points.index(points[0]), middle_points.index(points[1])
        assert abs(i1 - i2) == 1
    

