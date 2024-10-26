import random


def get_move(currx, curry):
    "return move chose by ai"
    choice = random.randint(1,6)
    if (choice == 1):
        #+1x
        return currx+1,curry
    elif (choice == 2):
        pass
        #+1 y
        return currx,curry+1
    elif (choice == 3):
        pass
        return currx+1,curry+1
        #+1 x, +1 y
    elif (choice == 4):
        return currx +1,curry-1
        #+1x, -1y
        pass
    elif(choice == 5):
        #-1x,+1y
        return currx-1,curry+1
        pass
    elif (choice == 6):
        return currx-1,curry-1
        #-1x,-1y
        pass