# -*- coding: utf-8 -*-
"""
Created on Tue Feb  1 18:56:45 2022

@author: steph 
"""
import numpy as np
import argparse
from cookworld import cookworld
import random


class cooker:
    def __init__(self, start, actions, world, discount, learning_rate, epsilon, lamb, adaptive_epsilon):
        self.actions = actions
        self.world = world
        self.qtable = {}
        self.eligibility = {}
        for i in range(world.row):
            for j in range(world.col):
                for k in [False, True]:
                    for a in self.actions:
                        self.qtable[(i, j, k, a)] = 0
                        self.eligibility[(i, j, k, a)] = 0
        self.start = start
        self.state = start
        self.discount = discount
        self.learning_rate = learning_rate
        self.epsilon = epsilon
        self.lamb = lamb
        self.adaptive_epsilon = adaptive_epsilon

    def choose_action(self):
        if (np.random.uniform(0, 1) < self.epsilon):
            action = np.random.choice(self.actions)
        else:
            action = self.max_action(self.state)
        return action

    def max_action(self, state):
        action = np.random.choice(self.actions)
        maxq = self.qtable[state+(action,)]
        for a in self.actions:
            q = self.qtable[state+(a,)]
            if q > maxq:
                maxq = q
                action = a
        return action

    def take_action(self, action):
        next_state = self.world.next_state(self.state, action)
        next_action = self.max_action(next_state)
        delta = (self.world.give_reward(next_state) + self.discount *self.qtable[next_state+(next_action,)]) - self.qtable[self.state+(action,)]
        self.eligibility[self.state+(action,)]+=1
        for i in range(self.world.row):
            for j in range(self.world.col):
                for k in [False, True]:
                    for a in self.actions:
                        self.qtable[(i, j, k, a)] += self.learning_rate * delta * self.eligibility[(i,j,k,a)]
                        self.eligibility[(i, j, k, a)] = self.eligibility[(i, j, k, a)] * self.discount * self.lamb
        self.state = next_state

    def update_epsilon(self,episode):
        self.epsilon = 1/episode

    def play(self, episodes):
        current_ep = 1
        while current_ep <= episodes:
            #print(self.state)
            
            if self.adaptive_epsilon:
                self.update_epsilon(current_ep)

            if self.world.reached_end(self.state):
                self.state = self.getRandomStart()
                print("Episode",current_ep,"Finished...",sep=" ")
                current_ep += 1
            else:
                action = self.choose_action()
                self.take_action(action)
                
    def getRandomStart(self):
        row = random.choice(range(self.world.row))
        col = random.choice(range(self.world.col))
        
        if (row, col) in [(0,4), (2, 4), (3,4)]:
            i = random.choice([-1, 1])
            
            return (row, col + i, False)
        if (row, col) in tools:
            return (row, col, True)
        else:
            return (row, col, False)
        

    def get_policy_sequence(self,start):
        state = start
        a = []
        while(not(self.world.reached_end(state))):
            action = self.max_action(state)
            a.append(action)
            state = self.world.next_state(state, action)
        return a

    def print_Q_table(self):
        print(self.qtable)

    def print_policy(self, start):
        print("Policy from start")
        state = start
        while(not(self.world.reached_end(state))):
            action = self.max_action(state)
            print(action, end=" -> ")
            state = self.world.next_state(state, action)
        print("X")
    
    def print_policy_grid(self):
        print("Policy for the grid")
        for r in range(self.world.row):
            for c in range(self.world.col):
                for has_tool in [False, True]:
                    state = (r, c, has_tool)
                    action = self.max_action(state)
                    print(state, action)

def convert_position(s):
    try:
        row,col = map(int,s.split(","))
        return (row,col)
    except:
        raise argparse.ArgumentTypeError("arguments must be row,col")


if __name__ == "__main__":
    
    walls = [
        ((0,0),(1,0)), ((0,1),(1,1)),
        ((0,2),(1,2)), ((0,3),(0,4)),
        ((0,4),(0,5)), ((0,7),(1,7)),
        ((1,1),(2,1)), ((1,2),(2,2)),
        ((1,4),(2,4)), ((1,6),(1,7)),
        ((2,0),(2,1)), ((2,3),(2,4)),
        ((2,4),(2,5)), ((2,6),(2,7)),
        ((2,7),(3,7)), ((2,8),(3,8)),
        ((3,3),(3,4)), ((3,4),(3,5)),
        ((2,0),(3,0)), ((0,4),(1,4))]
    #Arguments for world and agent
    parser = argparse.ArgumentParser(description='Train a cookingAgent to find the optimal path in a cookingWorld, that is taking a tool and start cooking as fast as possible.')
    parser.add_argument('--rows',"-y",default=4,type=int,help='Number of rows in the cook world e.g 10')
    parser.add_argument('--cols',"-x",default=9,type=int,help='Number of coloumns in the grid world e.g 10')
    parser.add_argument('--start',"-s",default=(1,4, False),type=convert_position,help='Starting position of the cookingAgent in the cookingWorld. Given as a tuple in the form of row,coloumn, has_tool e.g -s 0,0,False')
    parser.add_argument('--walls',"-o",default=walls,nargs='+',type=convert_position,help='Wals present in the cooking world. Given as a list of couple of tuples in the form ((row,coloumn),(row,coloumn)) e.g -o ((0,0),(1,0))')
    parser.add_argument('--tools',"-t",default=[(2,0), (2,7)],nargs='+',type=convert_position,help='Tools positions in the cooking world, given as a list of tuples in the form row,coloumn, row,coloumn e.g -r 9,9 0,9')
    parser.add_argument('--ends',"-e",default=[(3,0)],nargs='+',type=convert_position,help='Frying pans positions for the cooking world i.e the end states. Given as a list of tuples in the form row,coloumn row,coloumn e.g -e 9,9 0,9')
    parser.add_argument('--actions',"-a",default=["u", "d", "l", "r"],nargs='+',type=str,help='List of actions that the agent can perform. Given as a list of chars where "u" = Up, "r" = Right, "l" = Left, "d" = Down. Only actions from these 4 can be selected. e.g -a u d l r')
    parser.add_argument('--discount',"-d",default=0.9,type=float,help='Discount factor for future rewards i.e how much weight does the agent take the future into account. e.g -d 0.9')
    parser.add_argument('--learning_rate',"-l",default=0.1,type=float,help='Learning rate for the agent i.e how much does the agent take the learning error into account each step. e.g -l 0.1')
    parser.add_argument('--epsilon',"-ep",default=0.2,type=float,help='Epsilon value for the epsilon greedy policy i.e how much does the agent try to explore. e.g -ep 0.2')
    parser.add_argument('--adaptive_epsilon',"-ae",default=False,action='store_true',help='Choice to use Adaptive epsilon value i.e the exploratory nature of the agent decreases as the number of episodes played increases')
    parser.add_argument('--number_of_episodes',"-n",default=1000,type=int,help='Number of episodes that the agent will play to learn optimal policy e.g 100')
    parser.add_argument('--lambda_value',"-la",default=0.5,type=float,help='The lambda value for the agent i.e the weighting given to future steps in the sampled run e.g 0.5')
    parser.add_argument('--print_policy',"-pp",default=True,action='store_true',help='Choice of whether or not to print policy after simulated e.g True')
    parser.add_argument('--print_policy_grid',"-ppg",default=True,action='store_true',help='Choice of whether or not to print policy for each grid cell after simulated e.g True')

    args = parser.parse_args()
    
    start = args.start
    rows = args.rows
    cols = args.cols
    walls = args.walls
    tools = args.tools
    ends = args.ends

    world = cookworld(rows, cols, walls, tools, ends)
    
    actions = args.actions
    discount = args.discount
    learning_rate = args.learning_rate
    epsilon = args.epsilon
    number_of_episodes = args.number_of_episodes
    lamb = args.lambda_value
    adaptive_epsilon = args.adaptive_epsilon

    a = cooker(start, actions, world, discount, learning_rate, epsilon, lamb, adaptive_epsilon)
    
    a.play(number_of_episodes)
    
    #a.printQtable()
    
    if args.print_policy:
        a.print_policy(start)
    
    if args.print_policy_grid:
        a.print_policy_grid()

