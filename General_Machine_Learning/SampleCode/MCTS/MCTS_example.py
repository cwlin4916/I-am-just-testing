"""
The following code is to run the MCTS algorithm. 
The MCTS process starts with a root node representing the current game state. 
Then interatively: 
1 Selection: A tree policy is used to select a leaf node. This is usually UCB1. 
1a) We will repeat the selection process untiil we reach a node that does not have any children. This is also called a leaf node. 
We then consider two cases on whether the visit count (n) of the leaf node is greater than 0. 
1b) If we have previously vist the current leaf node. We run a simlutation, to step 2. 
1b) If we have not previously visited the current leaf node, n=0, we expand the current leaf node. 
2. Simulates: A simulation is run from the leaf node to a terminal state. 
3. Backpropagation: The result of the simulation is used to update the nodes on the path from the root to the leaf. 

"""

#Importing the necessary libraries
import math 
import copy
import random 
import numpy as np
import gynamsium as gym #This is the gym environment that we will be using 


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
        self.value=0  
        self.n = 0 
        self.state=state
        self.children = [] 
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
    
    # run n_iter, number of iterations 
    def run(self, n_iter =200):
        for _ in range (n_iter):
            value, node_path = self.traverse() #We traverse the tree. 
    
    def traverse(self):
        """
        
        """
        cur_node=self.root_node
        node_path=[cur_node]
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
                
            
"""Sample run
"""
if __name__ == '__main__':
    env=gym.make('CartPole-v0') #We create an instance of the CartPole environment.
    env.reset()
    done = False #We set done to False. 
    tot_reward  = 0 #We initialize the total reward to 0. 
    while not done: 
        mcts =MCTS(copy.deepcopy(env),reset=False) # We create an instance of the MCTS class. 
        probs=mcts.run(20)