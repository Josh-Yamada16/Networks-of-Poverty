import random
from Person import Person
from SocialLadder import SocialLadder
import Parameters as P
import time
import Sim_Setup

def generate_person(id):
    """Generate a person with random stats."""
    # Assuming person.py defines parameters like strength, intelligence, and charisma
    money = random.randint(1, 100)
    clout = random.randint(1, 100)
    rizz = random.randint(1, 100)
    return Person(id=id, money=money, clout=clout, rizz=rizz)

def run_sim(based_on, duration, interval, num_iterations):
    start_time = time.time()
    # Simulation based on iterations
    if based_on == "iteration":        
        for i in range(num_iterations):
            evaluate_life(social_ladder)
            print("Iteration:", i + 1)
            print(social_ladder)
            print()
    # Simulation based on time
    if based_on == "time":
        while time.time() - start_time < duration:
            evaluate_life(social_ladder)
            print(social_ladder)
            print()
            time.sleep(interval)

def evaluate_life(social_ladder):
    """Evaluate the life of each person."""
    move_up, move_down = 0, 0
    for level, people in social_ladder.get_ladder().items():
        if len(people) == 0:
            continue
        total_avg = (sum(p.get_money() for p in people) + sum(p.get_clout() for p in people) + sum(p.get_rizz() for p in people)) / len(people)
        for person in people:
            diff = total_avg - sum([person.get_money(), person.get_rizz(), person.get_clout()])
            if abs(diff) > 30 and diff < 0:
                person.change_status(-1)
            elif abs(diff) > 30 and diff > 0:
                person.change_status(1)
            else:
                person.change_status(0)

            # Move the person based on their status
            if person.status == person.EmotionalState.SUPERIOR:
                new_level = min(level + 1, 10)
                social_ladder.move_person(person, new_level)
                person.change_status(0)
                move_up += 1
            elif person.status == person.EmotionalState.INFERIOR:
                new_level = max(level - 1, 1)
                social_ladder.move_person(person, new_level)
                person.change_status(0)  # Reset status after moving
                move_down += 1
    print(f"People moved up: {move_up}, People moved down: {move_down}")

if __name__ == "__main__":
    run_sim(based_on=P.BASED_ON, duration=P.SIM_DURATION, interval=P.SIM_INTERVAL, num_iterations=P.NUM_ITERATIONS)
