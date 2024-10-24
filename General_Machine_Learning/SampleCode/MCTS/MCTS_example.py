"""
The following code is to run the MCTS algorithm. 
The MCTS process starts with a root node representing the current game state. 
Then interatively: 
1 Selection: A tree policy is used to select a leaf node. This is usually UCB1. 
We then consider two cases on whether the visit count (n) of the leaf node is greater than 0. 
1a) If we have previously vist the current leaf node. We run a simlutation, to step 2. 
1b) If we have not previously visited the current leaf node, n=0, we expand the current leaf node. 
2. Simulates: A simulation is run from the leaf node to a terminal state. 
3. Backpropagation: The result of the simulation is used to update the nodes on the path from the root to the leaf. 

"""

#Importing the necessary libraries
import math 
import copy
import random 
import numpy as np
import gymnasium as gym #This is the gym environment that we will be using 


"""
Below is the code for the node class. 
"""

class Node: 
    def __init__(self, state=None):
        """
        value: the sum of returns that were obtained by going through this node. 
        n: the number of times this node was visited. 
        state: the state represented by this node. 
        children: the children of this node.  
        """
        self.value=0   # total accumulated return of this node
        self.n = 0 # visit count 
        self.state=state # state represented by this node 
        self.children = [] #list of child notes 
    #method to calculate the UCB1 score of a child
    def get_child_ucb1(self, child):
        if child.n ==0:
            return float("inf") #If the child has not been visited, we return infinity. 
        else: 
            return child.value/child.n + 2*math.sqrt(math.log(self.n)/child.n) 
        # child.value/chald.n means the average return of the child. This is the exploitation term. 
    #method to calculate the child with the max UCB1 score and its index
    def get_max_ucb1_child(self):
        if not self.children: #If the node has no children, we return None. 
            return None
        max_i =0 #We initialize the index of the child with the max UCB1 score to 0. 
        max_ucb1 = float("-inf") #We initialize the max UCB1 score to negative infinity, because we want to maximize it. 
        for i, child in enumerate(self.children):
            ucb1 = self.get_child_ucb1(child)
            if ucb1 > max_ucb1: 
                max_ucb1 = ucb1
                max_i = i 
        return self.children[max_i], max_i #We return the child with the max UCB1 score and its index. 

"""
Below is code for MCTS class. This says which action to take next. 
For each new state, we create a new instance of the MCTS class.
Methods: 
run: run MCTS for a specified number of iterations. 
iterations: traverse the currently explored tree, expand if necessary. 
"""

class MCTS:
    def __init__(self, env, reset=False):
        """
        env: the environment that we are using to find the next best action.
        start_env: a copy of the environment that we are using.
        root_node: the root node of the tree that we are building. 
		"""
        self.env=env
        if reset: 
            start_state, _=self.env.reset() #We reset the environment and get the start state.
        else:
            start_state = self.env.unwrapped.state #We get the current state of the environment. 
        self.start_env =copy.deepcopy(self.env) #We create a copy of the environment.
        self.root_node= Node(start_state) #We create a node with the start state. 
    
        for act in range(self.env.action_space.n): # we first expand the root node by recursively acting all possible action 
            env_copy = copy.deepcopy(self.env) #We create a copy of the environment. 
            new_state, _, _, _ = env_copy.step(act) # The other return values are - reward (received after taking action), done (a boolean whether episode has ended), info. step(action) is a method by the gym environment for on time step. 
            new_node = Node(new_state) #We create a new node with the new state. 
            self.root_node.children.append(new_node) #We append the new node to the children of the root node. 
        
    
    # run n_iter, number of iterations 
    def run(self, n_iter =200):
        """
        Run the MCTS algorithm for a specified number of iterations. 
        Input: 
        self: the MCTS object. 
        n_iter: the number of iterations to run the MCTS algorithm. 
        Output: the action probabilities. 
        """
        for _ in range (n_iter):
            value, node_path = self.traverse() #We traverse the tree to find a leaf node
            self.backpropagate(node_path, value) #We backpropagate the value of the leaf node. 
            self.env = copy.deepcopy(self.start_env) #We reset the environment to the start environment. 
        #caluclate thea ction probabilities based on teh accumulated vlaues 
        val=[float("-inf")]*self.env.action_space.n #We initialize the value of the actions to negative infinity. 
        for i, child in enumerate(self.root_node.children):
            val[i]= (child.value/child.n) #We calculate the value of the action. 
        return np.exp(val)/np.sum(np.exp(val)) #We return the action probabilities. 
    
    def traverse(self):
        """
        The traverse method. We start fron the root node and traverse the tree until we reach a leaf node. 
        """
        cur_node=self.root_node # We set the current node to the root node. 
        node_path=[cur_node] #We initialize the node path to the current node, we will add in the nodes as we traverse the tree. 
        while cur_node.childern: # While the current node has children, we continue traversing the tree.
            cur_node, idx = cur_node.get_max_ucb1_child() #We get the child with the max UCB1 score.
            self.env.step(idx) # We take the action that corresponds to the child with the max UCB1 score.
            node_path.append(cur_node) #We append the current node to the node path.
        if cur_node.n:# If the current node has been visited, we run a simulation. 
            for act in range(self.env.action_space.n): #We iterate over the possible actions.
                env_copy = copy.deepcopy(self.env) #We create a copy of the environment. Deepcopy means that we create a new object with the same value as the current object. 
                new_state, _, _, _, _=  env_copy.step(act) #We take the action. 
                new_node = Node(new_state)
                cur_node.children.append(new_node) #We append the new node to the children of the current node.
            cur_node, idx = cur_node.get_max_ucb1_child() #We get the child with the max UCB1 score. 
            self.env.step(idx) # we take the action that corresponds to the child with the max UCB1 score, what does this do  
            node_path.append(cur_node)
        return self.rollout(), node_path 
    
    def rollout(self) -> float: 
        tot_reward = 0 
        while True: 
            act = random.randrange(self.env.action_space.n) #We choose a random action. 
            _, reward, done, _ = self.env.step(act) 
            tot_reward += reward 
            if done: 
                break
            return tot_reward
            
"""Sample run
"""
if __name__ == '__main__':
    env=gym.make('CartPole-v1') #We create an instance of the CartPole environment.
    env.reset() # We reset the environment. 
    done = False #We set done to False. 
    tot_reward  = 0 #We initialize the total reward to 0. 
    while not done: 
        mcts =MCTS(copy.deepcopy(env),reset=False) # We create an instance of the MCTS class. 
        probs=mcts.run(20) # We run the MCTS algorithm for 20 iterations. 
        action = random.choices(range(len(probs)), weights=probs, k=1)[0] #We choose an action based on the action probabilities. 
        
        _, reward, done, _, _= env.step(action) #We take the action. 
        tot_reward += reward # We update the total reward. 
        print(f"Action: {action}, Reward: {reward}, Total Reward: {tot_reward}", end='\r') #We print the action, reward, and total reward. 