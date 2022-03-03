# -*- coding: utf-8 -*-
"""
Created on Tue Feb  1 17:32:13 2022

@author: steph
"""
class cookworld:
# =============================================================================
#     s = (x, y, has_tool)
#     walls = [((x, y), (x, y)), ...]
#     tool = [(x,y), ...]
#     end = [(x,y,), ...]
# =============================================================================
    def __init__(self, row, col, walls, tools, ends):
        self.row = row
        self.col = col
        self.walls = walls
        self.tools = tools
        self.ends = ends
        
        self.reward = {}
        for i in range(row):
            for j in range(col):
                self.reward[(i,j,False)] = -1
                self.reward[(i,j,True)] = -1
            
        
        for t in tools:
            (row,col) = t
            self.reward[(row,col,False)]=10
        
        for e in ends:
            (row,col) = e
            self.reward[(row,col,True)]=100
        
    def give_reward(self, state):
        return self.reward[state]

    def reached_end(self, state):
        for s in self.ends:
            if state==s+(True,):
                return True
        return False

    def next_state(self, state, action):
        (row, col, has_tool) = state
        if action == "u":
            row += 1
            if row > self.row-1 or ((row-1,col),(row,col)) in self.walls or ((row,col),(row-1,col)) in self.walls:
                # se esco fuori o sbatto su un muro, resto sullo stato attuale
                return state
            elif has_tool or (row, col) in self.tools:
                # se avevo il tool mi sposto e lo mantengo, o se non lo avevo e
                # mi sposto su una cella dove c'è il tool, assumo che lo prendo 
                return (row, col, True)
            else:  
                # se non avevo il tool e non vado sul tool, mi sposto semplicemente
                return (row, col, False)
        if action == "d":
            row -= 1
            if row < 0 or ((row+1,col),(row,col)) in self.walls or ((row,col),(row+1,col)) in self.walls:
                return state
            elif has_tool or (row, col) in self.tools:
                return (row, col, True)
            else: 
                return (row, col, False)
        if action == "l":
            col -= 1
            if col < 0 or ((row,col+1),(row,col)) in self.walls or ((row,col),(row,col+1)) in self.walls:
                return state
            elif has_tool or (row, col) in self.tools:
                return (row, col, True)
            else: 
                return (row, col, False)
        if action == "r":
            col += 1
            if col > self.col-1 or ((row,col-1),(row,col)) in self.walls or ((row,col),(row,col-1)) in self.walls:
                return state
            elif has_tool or (row, col) in self.tools:
                return (row, col, True)
            else: 
                return (row, col, False)

        

             