behavior_b_dictionary = {
    0: "Neutral",
    1: "Aggressive",
    2: "Passive",
    3: "Cooperative",
    4: "Competitive",
    5: "Unpredictable"
}

class CentralNode:
    def __init__(self, node_id: int, name: str, influence: float, behavior_b: int, neighbors: set[Node]):
        self.node_id = node_id
        self.name = name
        self.influence = influence
        self.behavior_b = behavior_b


    def spread_behavior(self):
        pass