import matplotlib.pyplot as plt
import matplotlib.widgets as widgets
from matplotlib.patches import Rectangle
import random
import time
import sys

# Import AIMA search components
from search import EightPuzzle, astar_search

# -------------------------------------------------------------------------
# Configuration and Constants
# -------------------------------------------------------------------------
GOAL_STATE = (1, 2, 3, 4, 5, 6, 7, 8, 0)

# Vibrant, modern palette for each tile (1-8)
TILE_COLORS = {
    1: '#F72585', # Neon Pink
    2: '#7209B7', # Deep Purple
    3: '#3A0CA3', # Royal Blue
    4: '#4361EE', # Bright Blue
    5: '#4CC9F0', # Sky Blue
    6: '#FFBE0B', # Vivid Yellow
    7: '#FB5607', # Bright Orange
    8: '#FF006E', # Rose Red
}

# -------------------------------------------------------------------------
# Manhattan Heuristic Function
# -------------------------------------------------------------------------
def manhattan_distance(node):
    """Calculates the sum of Manhattan distances of tiles from their goal positions."""
    state = node.state
    dist = 0
    for i, val in enumerate(state):
        if val != 0:
            # Current position
            curr_r, curr_c = i // 3, i % 3
            # Goal position (val-1 gives the 0-indexed position for values 1-8)
            goal_r, goal_c = (val - 1) // 3, (val - 1) % 3
            dist += abs(curr_r - goal_r) + abs(curr_c - goal_c)
    return dist

# -------------------------------------------------------------------------
# Klotski GUI Class
# -------------------------------------------------------------------------
class KlotskiGUI:
    def __init__(self):
        self.state = list(GOAL_STATE)
        self.moves = 0
        self.animating = False
        
        # Setup Figure
        self.fig = plt.figure(figsize=(7, 9))
        self.fig.canvas.manager.set_window_title('AI-Powered Klotski Puzzle')
        self.fig.patch.set_facecolor('#1e1e1e') # Dark background
        
        # Board Axes
        self.ax = plt.axes([0.1, 0.25, 0.8, 0.65])
        self.ax.set_facecolor('#121212')
        self.ax.set_xlim(0, 3)
        self.ax.set_ylim(0, 3)
        self.ax.axis('off')
        self.ax.set_aspect('equal')
        
        # Initialize UI elements
        self.tile_patches = {}
        self.tile_texts = {}
        self.init_board_objects()
        
        # Connect click event
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        
        # Setup Buttons
        self.setup_buttons()
        
        self.update_display()
        
    def init_board_objects(self):
        """Creates the rectangle and text objects for each tile."""
        for val in range(1, 9):
            # Tile background
            rect = Rectangle((0, 0), 0.95, 0.95, color=TILE_COLORS[val], lw=2, ec='white', zorder=2)
            self.ax.add_patch(rect)
            # Tile number
            txt = self.ax.text(0, 0, str(val), ha='center', va='center', 
                               fontsize=36, fontweight='bold', color='white', zorder=3)
            self.tile_patches[val] = rect
            self.tile_texts[val] = txt

    def setup_buttons(self):
        """Creates the Shuffle and Solve buttons with matching palette colors."""
        # Shuffle Button
        ax_shuffle = plt.axes([0.15, 0.08, 0.3, 0.07])
        self.btn_shuffle = widgets.Button(ax_shuffle, 'Shuffle', color='#3A0CA3', hovercolor='#4361EE')
        self.btn_shuffle.label.set_color('white')
        self.btn_shuffle.label.set_fontsize(14)
        self.btn_shuffle.label.set_fontweight('bold')
        self.btn_shuffle.on_clicked(self.shuffle_action)
        
        # Solve Button
        ax_solve = plt.axes([0.55, 0.08, 0.3, 0.07])
        self.btn_solve = widgets.Button(ax_solve, 'Solve Using AI', color='#7209B7', hovercolor='#F72585')
        self.btn_solve.label.set_color('white')
        self.btn_solve.label.set_fontsize(14)
        self.btn_solve.label.set_fontweight('bold')
        self.btn_solve.on_clicked(self.solve_action)

    def get_pos(self, index):
        """Converts a flat index (0-8) to (x, y) board coordinates."""
        row, col = index // 3, index % 3
        # y is 2 - row because Matplotlib (0,0) is bottom-left
        return col + 0.025, (2 - row) + 0.025

    def update_display(self, title_color='white'):
        """Redraws the board based on the current state."""
        for i, val in enumerate(self.state):
            if val == 0:
                continue
            x, y = self.get_pos(i)
            self.tile_patches[val].set_xy((x, y))
            self.tile_texts[val].set_position((x + 0.475, y + 0.475))
            
        self.ax.set_title(f"Moves: {self.moves}", fontsize=20, color=title_color, pad=20)
        self.fig.canvas.draw_idle()

    def on_click(self, event):
        """Handles manual tile movement on click."""
        if self.animating or event.inaxes != self.ax:
            return
            
        col = int(event.xdata)
        row = int(2 - event.ydata) # invert y to get row
        
        if 0 <= row < 3 and 0 <= col < 3:
            clicked_idx = row * 3 + col
            self.try_move(clicked_idx)

    def try_move(self, idx):
        """Checks if a tile at idx can move into the empty space."""
        empty_idx = self.state.index(0)
        
        # Check adjacency (Manhattan distance == 1)
        r1, c1 = idx // 3, idx % 3
        r2, c2 = empty_idx // 3, empty_idx % 3
        
        if abs(r1 - r2) + abs(c1 - c2) == 1:
            self.state[empty_idx], self.state[idx] = self.state[idx], self.state[empty_idx]
            self.moves += 1
            self.update_display()
            
            if tuple(self.state) == GOAL_STATE:
                self.update_display(title_color='#33FF57')
                print("Congratulations! Solved.")

    def shuffle_action(self, event):
        """Shuffles the board into a random solvable state."""
        if self.animating: return
        
        print("Shuffling...")
        self.moves = 0
        state_list = list(GOAL_STATE)
        
        while True:
            random.shuffle(state_list)
            # Check solvability using the EightPuzzle class method
            prob = EightPuzzle(tuple(state_list))
            if prob.check_solvability(tuple(state_list)) and tuple(state_list) != GOAL_STATE:
                self.state = state_list
                break
        
        self.update_display()

    def solve_action(self, event):
        """Finds and executes the solution using A* search."""
        if self.animating: return
        
        if tuple(self.state) == GOAL_STATE:
            print("Already solved!")
            return
            
        self.animating = True
        self.ax.set_title("AI is thinking...", color='yellow', fontsize=20, pad=20)
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()
        
        print("Starting A* Search...")
        problem = EightPuzzle(tuple(self.state))
        
        # Run A* with Manhattan distance heuristic
        start_time = time.time()
        solution_node = astar_search(problem, h=manhattan_distance)
        end_time = time.time()
        
        if solution_node:
            path = solution_node.solution()
            print(f"Solution found in {len(path)} steps ({end_time - start_time:.2f}s).")
            
            # Animate the solution
            for action in path:
                # Get the state after this action to see where the blank moved
                # search.py Problem.result returns the new state
                new_state = problem.result(tuple(self.state), action)
                self.state = list(new_state)
                self.moves += 1
                self.update_display()
                plt.pause(0.2) # Small delay for animation
                
            self.update_display(title_color='#33FF57')
        else:
            print("No solution found!")
            self.ax.set_title("No Solution Found", color='red', fontsize=20, pad=20)
            
        self.animating = False

if __name__ == '__main__':
    # Add the current directory to sys.path to ensure local imports work
    import os
    sys.path.append(os.getcwd())
    
    gui = KlotskiGUI()
    plt.show()
