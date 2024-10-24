# Importing the necessary libraries
import math 
import copy
import random 
import numpy as np
import gymnasium as gym

class Node: 
    def __init__(self, state=None):
        self.value = 0
        self.n = 0
        self.state = state
        self.children = []

    def get_child_ucb1(self, child):
        if child.n == 0:
            return float("inf")
        else:
            return (child.value / child.n) + 2 * math.sqrt(math.log(self.n) / child.n)

    def get_max_ucb1_child(self):
        if not self.children:
            return None, None
        max_ucb1 = float("-inf")
        max_i = -1
        for i, child in enumerate(self.children):
            ucb1 = self.get_child_ucb1(child)
            if ucb1 > max_ucb1:
                max_ucb1 = ucb1
                max_i = i
        return self.children[max_i], max_i
class MCTS:
    def __init__(self, env, reset=False):
        self.env = env
        if reset:
            start_state, _ = self.env.reset()
        else:
            start_state = self.env.unwrapped.state
        self.start_env = copy.deepcopy(self.env)
        self.root_node = Node(start_state)

        for act in range(self.env.action_space.n):
            env_copy = copy.deepcopy(self.env)
            new_state, _, _, _, _ = env_copy.step(act)
            new_node = Node(new_state)
            self.root_node.children.append(new_node)

    def run(self, n_iter=200):
        for _ in range(n_iter):
            value, node_path = self.traverse()
            self.backpropagate(node_path, value)
            self.env = copy.deepcopy(self.start_env)
        vals = [float("-inf")] * self.env.action_space.n
        for i, child in enumerate(self.root_node.children):
            vals[i] = (child.value / child.n) if child.n else 0
        return np.exp(vals) / np.sum(np.exp(vals))

    def traverse(self):
        cur_node = self.root_node
        node_path = [cur_node]
        terminated = False
        truncated = False

        while cur_node.children and not (terminated or truncated):
            cur_node, idx = cur_node.get_max_ucb1_child()
            _, _, terminated, truncated, _ = self.env.step(idx)
            node_path.append(cur_node)
            if terminated or truncated:
                break

        if not (terminated or truncated) and cur_node.n:
            for act in range(self.env.action_space.n):
                env_copy = copy.deepcopy(self.env)
                new_state, _, _, _, _ = env_copy.step(act)
                new_node = Node(new_state)
                cur_node.children.append(new_node)
            cur_node, idx = cur_node.get_max_ucb1_child()
            _, _, terminated, truncated, _ = self.env.step(idx)
            node_path.append(cur_node)

        return self.rollout(terminated or truncated), node_path

    def rollout(self, env_terminated=False) -> float:
        tot_reward = 0
        if env_terminated:
            return tot_reward
        while True:
            act = random.randrange(self.env.action_space.n)
            _, reward, terminated, truncated, _ = self.env.step(act)
            tot_reward += reward
            if terminated or truncated:
                break
        return tot_reward

    def backpropagate(self, node_path: list, last_value: float):
        for node in reversed(node_path):
            node.value += last_value
            node.n += 1

if __name__ == '__main__':
    # Environment without rendering for MCTS
    env = gym.make('CartPole-v1')
    env.reset()
    
    # Environment with rendering for visualization
    render_env = gym.make('CartPole-v1', render_mode='human')
    render_env.reset()
    
    done = False
    tot_reward = 0
    while not done:
        # Perform MCTS to select the next action
        mcts = MCTS(copy.deepcopy(env), reset=False)
        probs = mcts.run(500)
        action = random.choices(range(len(probs)), weights=probs, k=1)[0]
        
        # Step both environments with the selected action
        _, reward, terminated, truncated, _ = env.step(action)
        render_env.step(action)
        
        tot_reward += reward
        done = terminated or truncated
        
        # Render the environment
        render_env.render()
        
        print(f"Action: {action}, Reward: {reward}, Total Reward: {tot_reward}", end='\r')
    
    env.close()
    render_env.close()