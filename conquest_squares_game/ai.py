import random

# return acceptable move chose by ai (random) (possibility : (0,1) : up, (1,0) : right, (0,-1) : down, (-1,0): left), without change data in the data base
def get_move():  
    return random.choice([{"x" : 1, "y":0}, {"x":-1, "y":0}, {"x":0, "y":1}, {"x":0 ,"y": -1}])

