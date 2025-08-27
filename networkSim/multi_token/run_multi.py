from networkSim.multi_token.multiSim import MultiTokenSimulation


def main():
    sim = MultiTokenSimulation(max_stingy_behaviors=10)
    states, layout, edge_mat = sim.run_simulation(iterations=5)
    print(f"Ran multi-token sim, produced {len(states)} states")

if __name__ == '__main__':
    main()
