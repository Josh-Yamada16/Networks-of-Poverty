from networkSim.multi_token.multiSim import MultiTokenSimulation


def test_multi_sim_instantiation():
    sim = MultiTokenSimulation()
    assert sim is not None
