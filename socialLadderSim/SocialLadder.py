class SocialLadder:
    def __init__(self):
        self.ladder = self.create_ladder()

    def add_person(self, person, level):
        self.ladder[level].append(person)

    def remove_person(self, person):
        for level in self.ladder:
            if person in self.ladder[level]:
                self.ladder[level].remove(person)
                break

    def move_person(self, person, new_level):
        """Move a person to a new level."""
        self.remove_person(person)
        self.add_person(person, new_level)

    def get_ladder(self):
        return self.ladder
    
    def create_ladder(self):
        """Create a social ladder with 10 levels."""
        ladder = {}
        for i in range(1, 11):
            ladder[i] = []
        return ladder

    def __str__(self):
        """String representation of the social ladder, printing each level and its corresponding person IDs."""
        result = "Social Ladder:\n"
        for level, people in self.ladder.items():
            # Collecting person IDs for each level
            person_ids = [person.get_id() for person in people]
            result += f"Level {level}: {person_ids}\n"
        return result.strip()

    def print_ladder(self):
        """Method to explicitly print each level with person IDs."""
        for level, people in self.ladder.items():
            person_ids = [person.get_id() for person in people]
            print(f"Level {level}: {person_ids}")