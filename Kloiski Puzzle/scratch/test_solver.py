from search import EightPuzzle, astar_search
import sys
import os

# Heuristic for testing
def manhattan_distance(node):
    state = node.state
    dist = 0
    for i, val in enumerate(state):
        if val != 0:
            curr_r, curr_c = i // 3, i % 3
            goal_r, goal_c = (val - 1) // 3, (val - 1) % 3
            dist += abs(curr_r - goal_r) + abs(curr_c - goal_c)
    return dist

# Test state (2 moves away from goal)
# Goal: (1, 2, 3, 4, 5, 6, 7, 8, 0)
# Test: (1, 2, 3, 4, 5, 0, 7, 8, 6) -> Move 6 down
#       (1, 2, 3, 4, 5, 6, 7, 8, 0) -> Goal
test_state = (1, 2, 3, 4, 5, 0, 7, 8, 6)

print(f"Testing A* solver with state: {test_state}")
problem = EightPuzzle(test_state)
solution_node = astar_search(problem, h=manhattan_distance)

if solution_node:
    path = solution_node.solution()
    print(f"Solution found: {path}")
    if path == ['DOWN']:
        print("Test PASSED")
    else:
        print(f"Unexpected path: {path}")
else:
    print("Test FAILED: No solution found")
