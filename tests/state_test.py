from blob import Blob
from chain import Chain
from point import Point
import state
def test_utility_functions():
    # 1 - - - 2
    # | \   / |
    # |  3-4  |
    # | /   \ |
    # 5 - - - 6 

    p1 = Point(0, 0)
    p2 = Point(1, 0)
    p3 = Point(0.3, 0.5)
    p4 = Point(0.7, 0.5)
    p5 = Point(0, 1)
    p6 = Point(1, 1)

    chain_12 = Chain.from_point_list([p1, p2])
    chain_26 = Chain.from_point_list([p2, p6])
    chain_65 = Chain.from_point_list([p6, p5])
    chain_51 = Chain.from_point_list([p5, p1])
    chain_13 = Chain.from_point_list([p1, p3])
    chain_24 = Chain.from_point_list([p2, p4])
    chain_64 = Chain.from_point_list([p6, p4])
    chain_53 = Chain.from_point_list([p5, p3])
    chain_34 = Chain.from_point_list([p3, p4])
    expected_chains =  {chain_12, chain_26, chain_65, chain_51, chain_13, chain_24, chain_64, chain_53, chain_34}

    blob_1243 = Blob.from_chain_loop([chain_12, chain_24, chain_34, chain_13])
    blob_264 = Blob.from_chain_loop([chain_26, chain_64, chain_24])
    blob_6435 = Blob.from_chain_loop([chain_64, chain_34, chain_53, chain_65])
    blob_135 = Blob.from_chain_loop([chain_13, chain_53, chain_51])

    blobs = [blob_1243, blob_264, blob_6435, blob_135]

    chains = state.get_chains_list(blobs)
    assert set(chains) == expected_chains, "get_chains_list returned incorrect chains"

    # Test `get_movable_chains`
    movable_chains = state.get_movable_chains(chains)
    expected_movable_chains = {chain_13, chain_24, chain_64, chain_53, chain_34}
    assert set(movable_chains) == expected_movable_chains, "get_movable_chains returned incorrect chains"

    # Test `get_movable_joints`
    movable_joints = state.get_movable_joints(movable_chains)
    expected_movable_joints = {p3, p4}
    assert set(movable_joints) == expected_movable_joints, "get_movable_joints returned incorrect points"
