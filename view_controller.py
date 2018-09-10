import time

from ui import GridWorldWindow
from mdp import GridMDP, value_iteration, policy_extraction, policy_evaluation, policy_iteration, values_converged, policy_converged

class ViewController(object):
    def __init__(self, metadata):
        self.gridworld = GridWorldWindow(metadata=metadata)
        self.mdp = GridMDP(metadata=metadata)

        # bind buttons
        self.gridworld.btn_value_iteration_1_step.configure(command=self._value_iteration_1_step)
        self.gridworld.btn_value_iteration_100_steps.configure(command=self._value_iteration_100_steps)
        self.gridworld.btn_value_iteration_slow.configure(command=self._value_iteration_slow)
        self.gridworld.btn_policy_iteration_1_step.configure(command=self._policy_iteration_1_step)
        self.gridworld.btn_policy_iteration_100_steps.configure(command=self._policy_iteration_100_steps)
        self.gridworld.btn_policy_iteration_slow.configure(command=self._policy_iteration_slow)

        self.gridworld.btn_reset.configure(command=self._reset_grid)

    def _value_iteration_1_step(self):
        values = value_iteration(self.mdp.values, self.mdp, num_iter=1)
        policy = policy_extraction(values, self.mdp)
        self.gridworld.update_grid(values, policy)
        self.mdp.update_values(values)
        self.mdp.update_policy(policy)
    
    def _value_iteration_100_steps(self):
        values = value_iteration(self.mdp.values, self.mdp, num_iter=100)
        policy = policy_extraction(values, self.mdp)
        self.gridworld.update_grid(values, policy)
        self.mdp.update_values(values)
        self.mdp.update_policy(policy)

    def _value_iteration_slow(self):
        # run one iteration of value iteration at a time
        old_values = dict(self.mdp.values)
        for i in range(100):
            values = value_iteration(self.mdp.values, self.mdp, num_iter=1)
            policy = policy_extraction(values, self.mdp)
            self.gridworld.update_grid(values, policy)
            self.mdp.update_values(values)
            self.mdp.update_policy(policy)

            self.gridworld.window.update()
            time.sleep(0.25)
            self.gridworld.window.update()

            new_values = dict(values)
            if values_converged(new_values, old_values):
                break

            old_values = new_values
        self.gridworld.show_dialog('Value Iteration has converged in {} steps!'.format(i+1))
    
    def _policy_iteration_1_step(self):
        policy, values = policy_iteration(self.mdp.policy, self.mdp, num_iter=1)
        self.gridworld.update_grid(values, policy)
        self.mdp.update_values(values)
        self.mdp.update_policy(policy)

    def _policy_iteration_100_steps(self):
        policy_iteration(self.mdp, num_iter=100)
        self.gridworld.update_grid(self.mdp.values, self.mdp.policy)

    def _policy_iteration_slow(self):
        # run one iteration of policy iteration at a time
        old_policy = dict(self.mdp.policy)
        for i in range(100):
            policy_iteration(self.mdp, num_iter=1)
            self.gridworld.update_grid(self.mdp.values, self.mdp.policy)
            self.gridworld.window.update()
            time.sleep(0.25)
            self.gridworld.window.update()

            new_policy = dict(self.mdp.policy)
            if policy_converged(new_policy, old_policy):
                break
            
            old_policy = new_policy
        self.gridworld.show_dialog('Policy Iteration has converged in {} steps!'.format(i+1))

    def _reset_grid(self):
        self.mdp.clear()
        self.gridworld.clear()

    def run(self):
        # main UI loop
        self.gridworld.run()
