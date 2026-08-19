import random
from cube_env import RubikEnv

class QLearningSolver:
    """
    A simple Q-learning demonstration class showing how reinforcement learning
    can learn to solve a Rubik's cube from simple, shallow scrambles.
    """
    def __init__(self, actions):
        self.actions = actions
        self.q_table = {}
        self.alpha = 0.2  # Learning rate
        self.gamma = 0.9  # Discount factor
        self.epsilon = 0.2  # Exploration rate

    def get_state_key(self, state):
        return tuple(state)

    def choose_action(self, state):
        state_key = self.get_state_key(state)
        if random.random() < self.epsilon or state_key not in self.q_table:
            return random.choice(self.actions)
        
        # Exploit: choose best action
        q_values = self.q_table[state_key]
        max_q = max(q_values.values())
        actions_with_max_q = [act for act, q in q_values.items() if q == max_q]
        return random.choice(actions_with_max_q)

    def update(self, state, action, reward, next_state):
        state_key = self.get_state_key(state)
        next_state_key = self.get_state_key(next_state)

        # Initialize Q-values if needed
        if state_key not in self.q_table:
            self.q_table[state_key] = {act: 0.0 for act in self.actions}
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = {act: 0.0 for act in self.actions}

        max_next_q = max(self.q_table[next_state_key].values())
        current_q = self.q_table[state_key][action]
        
        # Temporal difference target update
        self.q_table[state_key][action] = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)

def train_agent_demo():
    env = RubikEnv()
    moves = ['U', "U'", 'D', "D'", 'F', "F'", 'B', "B'", 'L', "L'", 'R', "R'"]
    agent = QLearningSolver(moves)

    print("Starting agent pretraining demo on shallow 2-step scrambles...")
    
    # Train over 1000 short episodes
    for episode in range(1001):
        env.reset()
        
        # Scramble 1-2 moves deep
        scramble_length = random.choice([1, 2])
        applied_scramble = []
        for _ in range(scramble_length):
            move = random.choice(moves)
            env.step(move)
            applied_scramble.append(move)

        state = env.get_state_flat().copy()
        
        # Maximum 5 moves allowed to solve it
        for step in range(5):
            action = agent.choose_action(state)
            next_state, reward, done, _ = env.step(action)
            agent.update(state, action, reward, next_state)
            state = next_state.copy()
            if done:
                break
                
    print(f"Pretraining complete. Explored {len(agent.q_table)} state-action spaces.")
    return agent
