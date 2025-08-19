from Person import Person

class Institution:
    def __init__(self):
        self.connections = {}

    def add_connection(self, person1: Person, cost: int):
        if person1 not in self.connections:
            self.connections[person1] = 0
        