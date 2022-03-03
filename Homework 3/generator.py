# -*- coding: utf-8 -*-
"""
Created on Tue Feb  1 21:43:32 2022

@author: steph
"""
import numpy as np
import pandas as pd

class generator:
    
    def __init__(self,
                 rows=4,
                 cols=9, 
                 walls=[((0,0),(1,0)), ((0,1),(1,1)), #((row, col),(row, col))
                     ((0,2),(1,2)), ((0,3),(0,4)),
                     ((0,4),(0,5)), ((0,7),(1,7)),
                     ((1,1),(2,1)), ((1,2),(2,2)),
                     ((1,4),(2,4)), ((1,6),(1,7)),
                     ((2,0),(2,1)), ((2,3),(2,4)),
                     ((2,4),(2,5)), ((2,6),(2,7)),
                     ((2,7),(3,7)), ((2,8),(3,8)),
                     ((3,3),(3,4)), ((3,4),(3,5)),
                     ((2,0),(3,0)), ((0,4),(1,4))],
                 tools=[(2,0), (2,7)],
                 frying_pans=[(3,0)],
                 ovens=[(3,7)],
                 tool_states=[False, True],
                 recipe_states=['scrambled', 'pudding'],
                 actions = ["u", "d", "l", "r"]):
                 
        self.rows = rows
        self.cols = cols         
        self.walls = walls
        self.tools = tools
        self.frying_pans = frying_pans
        self.ovens = ovens
        self.tool_states = tool_states
        self.recipe_states = recipe_states
        self.actions = actions



    # =============================================================================
    # state = (recipe_state, row, col, tool_state)
    # example: s=('pudding', 2, 0, True) -> the robot want to cook the eggs in the
    # oven (pudding), is in location (2,0) and has already the tool
    # =============================================================================
    
    def get_states(self):
        states = []
        for rs in self.recipe_states:
            for r in range(self.rows):
                for c in range(self.cols):
                    for ts in self.tool_states:
                        states.append((rs, r, c, ts))
         
        return states
    
    def gen_P(self, states):
        P = {}
        for s in states:
            for s_prime in states:
                for a in self.actions:
                    P[(s, s_prime, a)] = 0  
    
        for s in states:
            for a in self.actions:
                (recipe, row, col, has_tool) = s
                if a == "u":
                    self.gen_P_row(P, s, 1, "u", "u")
                if a == "d":
                    self.gen_P_row(P, s, 1, "d", "d")
                if a == "l":
                    self.gen_P_row(P, s, 1, "l", "l")
                if a == "r":
                    self.gen_P_row(P, s, 1, "r", "r")
        return P 

    def gen_P_tired(self, states):
        P_tired = {}
        for s in states:
            for s_prime in states:
                for a in self.actions:
                    P_tired[(s, s_prime, a)] = 0  
    
        for s in states:
            for a in self.actions:
                (recipe, row, col, has_tool) = s
                if a == "u":
                    # 0.6 vado l, 0.4 vado r
                    self.gen_P_row(P_tired, s, 0.6, "l", "u")
                    self.gen_P_row(P_tired, s, 0.4, "r", "u")
                        
                if a == "d":
                    # 0.6 vado r, 0.4 vado l
                    self.gen_P_row(P_tired, s, 0.6, "r", "d")
                    self.gen_P_row(P_tired, s, 0.4, "l", "d")
                    
                if a == "l":
                    # 0.6 vado d, 0.4 vado u 
                    self.gen_P_row(P_tired, s, 0.6, "d", "l")
                    self.gen_P_row(P_tired, s, 0.4, "u", "l")
                    
                if a == "r":
                    # 0.6 vado u, 0.4 vado d
                    self.gen_P_row(P_tired, s, 0.6, "u", "r")
                    self.gen_P_row(P_tired, s, 0.4, "d", "r")
        return P_tired                  
          
    def gen_P_row(self, P, s, prob, eval_a, orig_a):
        (recipe, row, col, has_tool) = s
        if eval_a == "u":
            row += 1
            if row > self.rows-1 or ((row-1,col),(row,col)) in self.walls or ((row,col),(row-1,col)) in self.walls:
                P[(s, s, orig_a)] = prob # rimango dove sono
            elif has_tool or (row, col) in self.tools:
                s_prime = (recipe, row, col, True)
                P[(s, s_prime, orig_a)] = prob # mi sposto e ho il tool
            else:  
                s_prime = (recipe, row, col, False)
                P[(s, s_prime, orig_a)] = prob # mi sposto e non ho il tool
                
        if eval_a == "d":
            # 0.6 vado r, 0.4 vado l
            row -= 1
            if row < 0 or ((row+1,col),(row,col)) in self.walls or ((row,col),(row+1,col)) in self.walls:
                P[(s, s, orig_a)] = prob # rimango dove sono
            elif has_tool or (row, col) in self.tools:
                s_prime = (recipe, row, col, True)
                P[(s, s_prime, orig_a)] = prob # mi sposto e ho il tool
            else:  
                s_prime = (recipe, row, col, False)
                P[(s, s_prime, orig_a)] = prob # mi sposto e non ho il tool
        if eval_a == "l":
            # 0.6 vado d, 0.4 vado u 
            col -= 1
            if col < 0 or ((row,col+1),(row,col)) in self.walls or ((row,col),(row,col+1)) in self.walls:
                P[(s, s, orig_a)] = prob # rimango dove sono
            elif has_tool or (row, col) in self.tools:
                s_prime = (recipe, row, col, True)
                P[(s, s_prime, orig_a)] = prob # mi sposto e ho il tool
            else:  
                s_prime = (recipe, row, col, False)
                P[(s, s_prime, orig_a)] = prob # mi sposto e non ho il tool
        if eval_a == "r":
            # 0.6 vado u, 0.4 vado d
            col += 1
            if col > self.cols-1 or ((row,col-1),(row,col)) in self.walls or ((row,col),(row,col-1)) in self.walls:
                P[(s, s, orig_a)] = prob # rimango dove sono
            elif has_tool or (row, col) in self.tools:
                s_prime = (recipe, row, col, True)
                P[(s, s_prime, orig_a)] = prob # mi sposto e ho il tool
            else:  
                s_prime = (recipe, row, col, False)
                P[(s, s_prime, orig_a)] = prob # mi sposto e non ho il tool

if __name__ == "__main__":
    gen = generator()
    states = gen.get_states()  

    P = gen.gen_P(states)         
    
    s = pd.Series(P, name='P')
    s.rename_axis((['s', 's_prime', 'a']), inplace=True)
    s.to_csv('P.csv')
    
    P_tired = gen.gen_P_tired(states)
    s_tired = pd.Series(P_tired, name='P_tired')
    s_tired.rename_axis((['s', 's_prime', 'a']), inplace=True)
    s_tired.to_csv('P_tired.csv')
                    


                

