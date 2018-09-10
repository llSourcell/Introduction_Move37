import random
from operator import add

MIN_DELTA = 1e-4

class GridMDP(object):
    def __init__(self, metadata):
        self.width = metadata['width']
        self.height = metadata['height']
        self.initial_value = metadata['initial_value']
        self.obstacles = metadata['obstacles']
        self.living_cost = metadata['living_cost']

        self.discount = metadata['discount']
        self.transition_distribution = metadata['transition_distribution']
        self.rewards = {tuple(terminal['state']) : terminal['reward'] for terminal in metadata['terminals']}
        self.terminals = list(self.rewards.keys())

        self._init_grid()

        # enumerate state space
        self.states = set()
        for row in range(self.height):
            for col in range(self.width):
                if self.grid[row][col] is not None:
                    self.states.add((row, col))
        
        # move one tile at a time
        self.actions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.num_actions = len(self.actions)

        # initialize values and policy
        self.policy = {}
        self.values = {}
        for state in self.states:
            self.values[state] = self.initial_value
            self.policy[state] = random.choice(self.actions)

    def R(self, state):
        if state in self.terminals:
            return self.rewards[state]
        else:
            # living cost
            return self.living_cost
    
    def _init_grid(self):
        self.grid = [[self.initial_value for col in range(self.width)] for row in range(self.height)]
        # apply obstacles
        for obstacle in self.obstacles:
            self.grid[obstacle[0]][obstacle[1]] = None

    def _move_forward(self, state, action):
        new_state = tuple(map(add, state, action))
        return new_state if new_state in self.states else state

    def _move_backward(self, state, action):
        new_action = self.actions[(self.actions.index(action) + 2) % self.num_actions]
        new_state = tuple(map(add, state, new_action))
        return new_state if new_state in self.states else state

    def _move_left(self, state, action):
        new_action = self.actions[(self.actions.index(action) - 1) % self.num_actions]
        new_state = tuple(map(add, state, new_action))
        return new_state if new_state in self.states else state

    def _move_right(self, state, action):
        new_action = self.actions[(self.actions.index(action) + 1) % self.num_actions]
        new_state = tuple(map(add, state, new_action))
        return new_state if new_state in self.states else state
    
    def allowed_actions(self, state):
        if state in self.terminals:
            return [None]
        else:
            return self.actions
    
    def next_state_distribution(self, state, action):
        if action == None:
            return [(0.0, state)]
        else:
            return [(self.transition_distribution['forward'], self._move_forward(state, action)),
                    (self.transition_distribution['left'], self._move_left(state, action)),
                    (self.transition_distribution['right'], self._move_right(state, action)),
                    (self.transition_distribution['backward'], self._move_backward(state, action))]
    
    def update_values(self, values):
        self.values = values
    
    def update_policy(self, policy):
        self.policy = policy

    def clear(self):
        self._init_grid()
        for state in self.states:
            self.values[state] = self.initial_value
            self.policy[state] = random.choice(self.actions)

def _expected_value(state, action, values, mdp):
    return sum([prob * values[new_state] for prob, new_state in mdp.next_state_distribution(state, action)])

def values_converged(new_values, old_values):
    sum_abs_diff = sum([abs(new_values[state] - old_values[state]) for state in new_values.keys()])
    return sum_abs_diff < MIN_DELTA

def policy_converged(new_policy, old_policy):
    same_action_for_state = [new_policy[state] == old_policy[state] for state in new_policy.keys()]
    return all(same_action_for_state)

def value_iteration(initial_values, mdp, num_iter=100):
    # initialize values
    values = initial_values
    
    for _ in range(num_iter):
        """
        We're making a copy so newly updated values don't affect each other.
        In practice, the values converge to the same thing, but I've added this here 
        in case you want to step through the values iteration-by-iteration.
        """
        new_values = dict(values)
        for state in mdp.states:
            new_values[state] = mdp.R(state) + mdp.discount * max([_expected_value(state, action, values, mdp) for action in mdp.allowed_actions(state)])
        
        if values_converged(new_values, values):
            break
        
        # update values for next iteration
        values = new_values

    return values
        
def policy_extraction(values, mdp):
    policy = {}
    for state in mdp.states:
        # we don't need to compute the full mdp.R(state) + mdp.discount * ... since mdp.R(state) and mdp.discount are constant given a state
        expected_values = [_expected_value(state, action, values, mdp) for action in mdp.allowed_actions(state)]
        action_idx, _ = max(enumerate(expected_values), key=lambda ev: ev[1])
        policy[state] = mdp.actions[action_idx]
    return policy

def policy_evaluation(policy, values, mdp, num_iter=50):
    for _ in range(num_iter):
        for state in mdp.states:
            values[state] = mdp.R(state) + mdp.discount * _expected_value(state, policy[state], values, mdp)

    return values

def policy_iteration(initial_policy, mdp, num_iter=100):
    policy = initial_policy
    values = {state: 0 for state in mdp.states}

    for _ in range(num_iter):
        new_policy = dict(policy)

        values = policy_evaluation(policy, values, mdp)
        unchanged_policy = True
        for state in mdp.states:
            expected_values = [_expected_value(state, action, values, mdp) for action in mdp.allowed_actions(state)]
            action_idx, _ = max(enumerate(expected_values), key=lambda ev: ev[1])
            action = mdp.actions[action_idx]
            if action != new_policy[state]:
                new_policy[state] = action
                unchanged_policy = False

        policy = new_policy

        if unchanged_policy:
            break
    
    return policy, values

